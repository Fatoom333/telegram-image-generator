export type GenerationStatus = "pending" | "in_progress" | "completed" | "failed";

export interface MeResponse {
    id: number;
    firstName: string;
    username?: string;
    balance: number;
}

export interface Generation {
    id: string;
    prompt: string;
    status: GenerationStatus;
    resultName?: string | null;
    resultUrl?: string | null;
    createdAt: string;
    cost: number;
    sourceImagesUrls?: string[];
}
