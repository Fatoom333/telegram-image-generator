import type { AIModelResponse } from "../api/types";

export function makeModelKey(model: AIModelResponse): string {
  return `${model.provider}:${model.model_name}`;
}