import type { MeResponse } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:3000"; // add url to env later

// get current user info
export async function getMe(token: string): Promise<MeResponse> {
    const response = await fetch(`${BASE_URL}/me`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${response.status}`);
    }
    const data: MeResponse = await response.json();
    return data;
}

