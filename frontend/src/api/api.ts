import type {
  AIModelResponse,
  BalanceResponse,
  GenerationResponse,
  PurchaseResponse,
  TariffResponse,
  UserResponse,
} from "./types";

const API_PREFIX = "/api";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        ready?: () => void;
        expand?: () => void;
        openLink?: (url: string) => void;
        showAlert?: (message: string) => void;
      };
    };
  }
}

type RequestOptions = RequestInit & {
  auth?: boolean;
};

function getTelegramInitData(): string {
  return window.Telegram?.WebApp?.initData ?? "";
}

function buildHeaders(options?: RequestOptions): Headers {
  const headers = new Headers(options?.headers);

  if (options?.auth !== false) {
    const initData = getTelegramInitData();

    if (initData) {
      headers.set("X-Telegram-Init-Data", initData);
    }
  }

  return headers;
}

async function requestJson<T>(path: string, options?: RequestOptions): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers: buildHeaders(options),
  });

  if (!response.ok) {
    let message = `Ошибка API: ${response.status}`;

    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      const text = await response.text();
      message = text || message;
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function getMe(): Promise<UserResponse> {
  return requestJson<UserResponse>("/me");
}

export function getBalance(): Promise<BalanceResponse> {
  return requestJson<BalanceResponse>("/balance");
}

export function listModels(): Promise<AIModelResponse[]> {
  return requestJson<AIModelResponse[]>("/ai/models", { auth: false });
}

export function listGenerations(limit = 20, offset = 0): Promise<GenerationResponse[]> {
  return requestJson<GenerationResponse[]>(`/generations?limit=${limit}&offset=${offset}`);
}

export function getGeneration(generationId: string): Promise<GenerationResponse> {
  return requestJson<GenerationResponse>(`/generations/${generationId}`);
}

export async function createGeneration(params: {
  prompt: string;
  provider?: string | null;
  modelName?: string | null;
  images?: File[];
}): Promise<GenerationResponse> {
  const formData = new FormData();

  formData.append("prompt", params.prompt.trim());

  if (params.provider) {
    formData.append("provider", params.provider);
  }

  if (params.modelName) {
    formData.append("model_name", params.modelName);
  }

  for (const image of params.images ?? []) {
    formData.append("images", image);
  }

  return requestJson<GenerationResponse>("/generations", {
    method: "POST",
    body: formData,
  });
}

export function listTariffs(): Promise<TariffResponse[]> {
  return requestJson<TariffResponse[]>("/purchases/tariffs", { auth: false });
}

export function createPurchase(tariffId: string): Promise<PurchaseResponse> {
  return requestJson<PurchaseResponse>("/purchases", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tariff_id: tariffId }),
  });
}

export function absoluteApiUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  return `${window.location.origin}${normalizedPath}`;
}
