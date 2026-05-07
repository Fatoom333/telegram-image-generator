export type GenerationStatus = "query" | "successful" | "failed";
export type TransactionType = "grant" | "spend" | "refund" | "purchase" | "admin_adjustment";
export type GenerationRole = "reference" | "generated";
export type PurchaseStatus = "created" | "succeeded" | "failed" | "cancelled" | "manual";

export interface RequestOptions {
    token?: string;
};

export interface GetRequestOptions extends RequestOptions {
    params?: Record<string, string | number | boolean | undefined>;
};

export interface ValidationError { 
    loc: (string | number)[];
    msg: string;
    type: string;
    input?: unknown;
    ctx?: Record<string, unknown>;
};

export interface ErrorResponse {
    detail?: string | ValidationError[];
};

export interface MeResponse {
    telegram_id: number;
    username: string | null;
    first_name: string | null;
    credits: number;
    is_banned: boolean;
};

export interface BalanceResponse {
    credits: number;
};

export interface TransactionResponse {
    id: string;
    type: TransactionType;
    amount: number;
    balance_after: number;
    reason: string | null;
    generation_id: string | null;
    created_at: string;
};

export interface AiModelResponse {
    provider: string;
    model_name: string;
    title: string;
    cost_credits: number;
    image_cost_credits: number;
    max_input_images: number;
};

export interface GenerationRequest {
    prompt: string;
    provider?: string | null;
    model_name?: string | null;
    images?: string[] | null;
};

export interface GenerationImageResponse {
    id: string;
    role: GenerationRole;
    file_url?: string | null;
    mime_type: string | null;
    created_at: string;
};

export interface GenerationResponse {
    id: string;
    telegram_id: number;
    prompt: string;
    status: GenerationStatus;
    provider: string | null;
    model_name: string | null;
    input_images_cnt: number;
    cost_credits: number;
    error_code: string | null;
    error_message: string | null;
    latensy_ms: number | null;
    craeted_at: string;
    updated_at: string;
    images?: GenerationImageResponse[];
};

export interface TariffResponse {
    id: string;
    title: string;
    amount_rub: number;
    credits: number;
    provider: string;
}

export interface PurchaseRequest {
    tariff_id: string;
}

export interface PurchaseResponse {
    if: string;
    telegram_id: number;
    amount_rub: number;
    credits: number;
    status: PurchaseStatus;
    provider: string;
    provider_payment_id: string | null;
    payment_url: string | null;
    created_at: string;
    updated_at: string;
}
