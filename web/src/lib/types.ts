export interface Category {
  id: string;
  name: string;
  slug: string;
  display_order: number;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price: number;
  sale_price: number | null;
  category_id: string;
  image_url: string | null;
  ingredients: string[];
  ingredient_details: IngredientDetail[] | null;
  is_vegan_certified: boolean;
  stock_quantity: number;
  category?: Category;
}

export interface IngredientDetail {
  name: string;
  role: string;
  origin: string;
  grade: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface Order {
  id: string;
  order_number: string;
  status: string;
  total_amount: number;
  discount_amount: number;
  shipping_fee: number;
  ordered_at: string;
}

export interface Review {
  id: string;
  user_id: string;
  product_id: string;
  rating: number;
  content: string | null;
  created_at: string;
  user?: { name: string };
}
