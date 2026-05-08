export type UserResponse = {
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  credits: number;
  is_banned: boolean;
};

export type BalanceResponse = {
  credits: number;
};

export type AIModelResponse = {
  provider: string;
  model_name: string;
  title: string;
  cost_credits: number;
  image_cost_credits: number;
  max_input_images: number;
};

export type GenerationImageResponse = {
  id: string;
  role: string;
  file_url: string | null;
  mime_type: string | null;
  created_at: string;
};

export type GenerationResponse = {
  id: string;
  telegram_id: number;
  prompt: string;
  status: string;
  provider: string | null;
  model_name: string | null;
  input_images_cnt: number;
  cost_credits: number;
  error_code: string | null;
  error_message: string | null;
  latency_ms: number | null;
  created_at: string;
  updated_at: string;
  images: GenerationImageResponse[];
};

export type TariffResponse = {
  id: string;
  title: string;
  amount_rub: number;
  credits: number;
  provider: string;
};

export type PurchaseResponse = {
  id: string;
  telegram_id: number;
  amount_rub: number;
  credits: number;
  status: string;
  provider: string;
  provider_payment_id: string | null;
  payment_url: string | null;
  created_at: string;
  updated_at: string;
};