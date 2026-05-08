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

  const rawText = await response.text();
  const parsedBody = parseResponseBody(rawText);

  if (!response.ok) {
    throw new Error(extractApiError(parsedBody, response.status));
  }

  return parsedBody as T;
}

function parseResponseBody(rawText: string): unknown {
  if (!rawText) {
    return null;
  }

  try {
    return JSON.parse(rawText);
  } catch {
    return rawText;
  }
}

function extractApiError(body: unknown, status: number): string {
  if (typeof body === "string" && body.trim()) {
    return body;
  }

  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail?: unknown }).detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }

          return String(item);
        })
        .join("; ");
    }
  }

  return `Ошибка API: ${status}`;
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

export function createGeneration(params: {
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
