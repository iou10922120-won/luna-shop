import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-[#2C3E6B] text-white/80">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold text-white tracking-wider mb-3">
              LUNA
            </h3>
            <p className="text-sm leading-relaxed">
              달빛처럼, 투명하게.
              <br />
              자연 유래 성분의 비건 스킨케어.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-3">쇼핑</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/products" className="hover:text-white transition-colors">
                  전체 상품
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  브랜드 스토리
                </Link>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-3">고객 지원</h4>
            <ul className="space-y-2 text-sm">
              <li>이메일: hello@luna-beauty.kr</li>
              <li>운영시간: 평일 10:00 - 18:00</li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/20 text-xs text-white/50 text-center">
          &copy; 2026 LUNA. All rights reserved. | 포트폴리오 목적의 가상 브랜드입니다.
        </div>
      </div>
    </footer>
  );
}
