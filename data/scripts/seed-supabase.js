const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// service_role 키로 연결 (테이블 생성 + RLS 우회)
// 환경변수: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Missing env: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());

  function parseLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && i + 1 < line.length && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    result.push(current);
    return result;
  }

  return lines.slice(1).map(line => {
    const values = parseLine(line);
    const obj = {};
    headers.forEach((h, i) => {
      let val = (values[i] || '').trim();
      if (val === '' || val === 'None') { obj[h] = null; return; }
      if (val === 'True') { obj[h] = true; return; }
      if (val === 'False') { obj[h] = false; return; }
      if ((val.startsWith('[') || val.startsWith('{')) && (val.endsWith(']') || val.endsWith('}'))) {
        try { obj[h] = JSON.parse(val); return; } catch (e) {}
      }
      const noNumCols = ['id', 'slug', 'phone', 'url', 'image', 'user_id', 'product_id', 'order_id', 'category_id', 'email', 'name', 'address'];
      if (/^\d+(\.\d+)?$/.test(val) && !noNumCols.some(c => h.includes(c))) {
        obj[h] = parseFloat(val);
        return;
      }
      obj[h] = val;
    });
    return obj;
  });
}

async function run() {
  // 1. 테이블 생성 (schema.sql 실행)
  console.log('=== Step 1: Creating tables ===');
  const schemaSql = fs.readFileSync(path.resolve(__dirname, 'schema.sql'), 'utf-8');

  // SQL을 개별 문장으로 분리해서 실행
  const statements = schemaSql
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0 && !s.startsWith('--'));

  for (const stmt of statements) {
    const { error } = await supabase.rpc('exec_sql', { sql: stmt + ';' });
    if (error) {
      // rpc가 없으면 REST API로는 DDL 실행 불가 — 안내
      if (error.message.includes('exec_sql')) {
        console.log('DDL via RPC not available. Trying direct SQL via fetch...');
        break;
      }
      console.log('SQL Error:', error.message);
    }
  }

  // REST API로 DDL 실행 (Supabase Management API 대신 pg-meta 사용)
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/exec_sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
    },
    body: JSON.stringify({ sql: schemaSql }),
  });

  if (!res.ok) {
    console.log('Cannot execute DDL via REST API.');
    console.log('Please run schema.sql in Supabase SQL Editor first.');
    console.log('Then re-run this script to seed data.\n');

    // 테이블 존재 여부 확인
    const { error: checkErr } = await supabase.from('categories').select('id').limit(1);
    if (checkErr && checkErr.message.includes('schema cache')) {
      console.log('Tables do NOT exist yet. Please run schema.sql first.');
      process.exit(1);
    }
    console.log('Tables exist! Proceeding with data seeding...\n');
  } else {
    console.log('Tables created successfully!\n');
  }

  // 2. 데이터 삽입
  console.log('=== Step 2: Seeding data ===');
  const csvDir = path.resolve(__dirname, '../csv');

  const tables = [
    { name: 'categories', file: 'categories.csv' },
    { name: 'products', file: 'products.csv' },
    { name: 'users', file: 'users.csv' },
    { name: 'orders', file: 'orders.csv' },
    { name: 'order_items', file: 'order_items.csv' },
    { name: 'reviews', file: 'reviews.csv' },
    { name: 'sessions', file: 'sessions.csv' },
    { name: 'inventory', file: 'inventory.csv' },
  ];

  for (const t of tables) {
    const filePath = path.join(csvDir, t.file);
    if (!fs.existsSync(filePath)) {
      console.log(`SKIP: ${t.file} not found`);
      continue;
    }

    const rows = parseCSV(filePath);
    console.log(`Inserting ${t.name}... (${rows.length} rows)`);

    let success = true;
    for (let i = 0; i < rows.length; i += 50) {
      const batch = rows.slice(i, i + 50);
      const { error } = await supabase.from(t.name).insert(batch);
      if (error) {
        console.log(`  ERROR at batch ${i}: ${error.message}`);
        success = false;
        break;
      }
    }
    console.log(`  -> ${t.name} ${success ? 'OK' : 'FAILED'}`);
  }

  console.log('\nDone!');
}

run();
