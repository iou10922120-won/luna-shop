export enum AnalyticsEvent {
  SESSION_START = 'session_start',
  PAGE_VIEW = 'page_view',
  PRODUCT_LIST_VIEW = 'product_list_view',
  PRODUCT_LIST_FILTER = 'product_list_filter',
  PRODUCT_VIEW = 'product_view',
  INGREDIENT_VIEW = 'ingredient_view',
  ADD_TO_CART = 'add_to_cart',
  REMOVE_FROM_CART = 'remove_from_cart',
  CART_VIEW = 'cart_view',
  CHECKOUT_START = 'checkout_start',
  PURCHASE = 'purchase',
  SIGNUP_START = 'signup_start',
  SIGNUP_COMPLETE = 'signup_complete',
  LOGIN = 'login',
  REVIEW_WRITE = 'review_write',
  COUPON_APPLY = 'coupon_apply',
}

export interface PageViewProps {
  page_path: string;
  page_title: string;
}

export interface ProductViewProps {
  product_id: string;
  product_name: string;
  category: string;
  price: number;
  sale_price: number | null;
}

export interface AddToCartProps {
  product_id: string;
  product_name: string;
  category: string;
  price: number;
  quantity: number;
  cart_total: number;
  cart_item_count: number;
}

export interface RemoveFromCartProps {
  product_id: string;
  product_name: string;
}

export interface PurchaseProps {
  order_id: string;
  order_number: string;
  total_amount: number;
  discount_amount: number;
  shipping_fee: number;
  item_count: number;
  items: Array<{
    product_id: string;
    category: string;
    quantity: number;
    price: number;
  }>;
  coupon_code?: string;
  payment_method: string;
}

export interface ProductListFilterProps {
  filter_type: string;
  filter_value: string;
}

export interface CheckoutStartProps {
  cart_total: number;
  item_count: number;
}

export interface LoginProps {
  method: string;
}

export type EventPropertiesMap = {
  [AnalyticsEvent.SESSION_START]: Record<string, never>;
  [AnalyticsEvent.PAGE_VIEW]: PageViewProps;
  [AnalyticsEvent.PRODUCT_LIST_VIEW]: { category?: string };
  [AnalyticsEvent.PRODUCT_LIST_FILTER]: ProductListFilterProps;
  [AnalyticsEvent.PRODUCT_VIEW]: ProductViewProps;
  [AnalyticsEvent.INGREDIENT_VIEW]: { product_id: string; product_name: string };
  [AnalyticsEvent.ADD_TO_CART]: AddToCartProps;
  [AnalyticsEvent.REMOVE_FROM_CART]: RemoveFromCartProps;
  [AnalyticsEvent.CART_VIEW]: { cart_total: number; item_count: number };
  [AnalyticsEvent.CHECKOUT_START]: CheckoutStartProps;
  [AnalyticsEvent.PURCHASE]: PurchaseProps;
  [AnalyticsEvent.SIGNUP_START]: Record<string, never>;
  [AnalyticsEvent.SIGNUP_COMPLETE]: Record<string, never>;
  [AnalyticsEvent.LOGIN]: LoginProps;
  [AnalyticsEvent.REVIEW_WRITE]: { product_id: string; rating: number };
  [AnalyticsEvent.COUPON_APPLY]: { coupon_code: string; discount_amount: number };
};
