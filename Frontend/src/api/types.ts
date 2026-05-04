export type GenerationStatus = "pending" | "in_progress" | "completed" | "failed";

export interface MeResponse {
    id: number;
    first_name: string;
    username?: string;
    balance: number;
}

export interface Generation {
    id: string;
    prompt: string;
    status: GenerationStatus;
    result_name?: string | null;
    result_url?: string | null;
    created_at: string;
    cost: number;
    source_images?: string[];
}
