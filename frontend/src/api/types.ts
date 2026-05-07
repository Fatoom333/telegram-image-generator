export type GenerationStatus = "pending" | "in_progress" | "completed" | "failed";

export interface MeResponse {
    tgId: number;
    username?: string;
    firstName?: string;
    credits: number;
    isBanned: boolean;
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
