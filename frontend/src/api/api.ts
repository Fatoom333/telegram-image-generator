import type { RequestOptions, GetRequestOptions, ErrorResponse, PurchaseResponse } from "./types";
import type { MeResponse, BalanceResponse, TransactionResponse, AiModelResponse } from "./types";
import type { GenerationResponse, GenerationRequest, TariffResponse, PurchaseRequest } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"; // add url to env later

// unvirsal response handler for both GET and POST requests

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const err: ErrorResponse = await response.json().catch(() => ({}));
        let msg = `Error ${response.status}`;
        if (err.detail) {
            if (Array.isArray(err.detail)) {
                msg = err.detail.map((e) => `${e.msg} (${e.loc.join('.')})`).join('; ');
            } else if (typeof err.detail === 'string') {
                msg = err.detail;
            }
        }
        throw new Error(msg);
    }
    return response.json() as Promise<T>;
};

export async function apiGet<T>(endpoint: string, options: GetRequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {};
    if (options.token) {
        headers['Authorization'] = `Bearer ${options.token}`;
    }
    let url = `${BASE_URL}${endpoint}`;
    if (options.params) {
        const queryParams = new URLSearchParams();
        Object.entries(options.params).forEach(([key, value]) => {
            if (value !== undefined) {
                queryParams.append(key, String(value));
            }
        });
        const qs = queryParams.toString();
        if (qs) {
            url += `?${qs}`;
        }
    }
    const response = await fetch(url, { method: 'GET', headers });
    return handleResponse<T>(response);
};

export async function apiPost<T>(endpoint: string, body: unknown, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (options.token) {
        headers['Authorization'] = `Bearer ${options.token}`;
    }
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body)
    });
    return handleResponse<T>(response);
};

// health check
export const checkHealth = async (): Promise<boolean> => {
    try {
        await apiGet<unknown>('/health');
        return Promise.resolve(true);
    } catch {
        return Promise.resolve(false);
    }
};

// get current user info
export const getMe = async (token: string): Promise<MeResponse> =>
    apiGet<MeResponse>('/api/me', { token });

// get user balance info
export const getBalance = async (token: string): Promise<BalanceResponse> =>
    apiGet<BalanceResponse>('/api/balance', { token });

// get all credits transactions for current user
export const getTransactions = async (token: string, limit: number, offset: number): Promise<TransactionResponse[]> =>
    apiGet<TransactionResponse[]>('/api/credits/transactions', {
        token,
        params: { limit, offset }
    });

// get all ai models
export const getModels = async (): Promise<AiModelResponse[]> =>
    apiGet<AiModelResponse[]>('/api/ai/models');

// create generation
export const postGeneration = async (token: string, generationRequest: GenerationRequest): Promise<GenerationResponse> =>
    apiPost<GenerationResponse>('/api/generations', generationRequest, { token });

// get generation list
export const getGenerations = async (token: string, limit: number, offset: number): Promise<GenerationResponse[]> =>
    apiGet<GenerationResponse[]>('/api/generations', {
        token,
        params: { limit, offset }
    });

// get generation by id
export const getGenerationById = async (token: string, generationId: string): Promise<GenerationResponse> =>
    apiGet<GenerationResponse>(`/api/generations/${generationId}`, { token });

// get generation image by generation id and image id
export const getGenerationImage = async (token: string, generationId: string, imageId: string): Promise<string> =>
    apiGet<string>(`/api/generations/${generationId}/images/${imageId}`, { token });

// get tariffs list
export const getTariffs = async (): Promise<TariffResponse[]> =>
    apiGet<TariffResponse[]>(`/api/purchases/tariffs`);

// create a purchase
export const postPurchase = async (token: string, purchaseRequest: PurchaseRequest): Promise<PurchaseResponse> =>
    apiPost<PurchaseResponse>('/api/purchases', purchaseRequest, { token });

// get list of purchases
export const getPurchases = async (token: string, limit: number, offset: number): Promise<PurchaseResponse[]> =>
    apiGet<PurchaseResponse[]>('/api/purchases', {
        token,
        params: { limit, offset }
    });
