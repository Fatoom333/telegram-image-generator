import { CardHeader } from "./misc/CardHeader";
import type { AIModelResponse } from "../api/types";
import { MAX_REFERENCE_IMAGES } from "../misc/constants";
import GenIcon from "../assets/gen_icon.svg?react";

type Props = {
    prompt: string;
    onPromptChange: (value: string) => void;
    models: AIModelResponse[];
    selectedModelKey: string;
    onModelChange: (key: string) => void;
    selectedModel: AIModelResponse | null;
    files: File[];
    onFilesChange: (files: FileList | null) => void;
    fileInputRef: React.RefObject<HTMLInputElement | null>;
    error: string | null;
    notice: string | null;
    isGenerating: boolean;
    isBootLoading: boolean;
    onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
};

export function GenerationForm({
    prompt,
    onPromptChange, 
    models, 
    selectedModelKey, 
    onModelChange, 
    selectedModel, 
    files, 
    onFilesChange, 
    fileInputRef, 
    error, 
    notice, 
    isGenerating, 
    isBootLoading, 
    onSubmit}: Props) {
    return (
        <div className="generation-form-card card">
            <CardHeader
                icon={<GenIcon/>}
                title="Новая генерация"
            />
            <form onSubmit={onSubmit}>
                <label className="sr-only" htmlFor="prompt">Промпт</label>
                <textarea
                    id="prompt"
                    maxLength={2000}
                    onChange={(event) => onPromptChange(event.target.value)}
                    placeholder="Введите промпт... (Например: Банан танцует танго)"
                    value={prompt}
                />
                <div className="form-grid">
                    <label className="field-label">Модель
                        <select
                            onChange={(event) => onModelChange(event.target.value)}
                            value={selectedModelKey}
                        >
                            {models.length === 0 ? (
                                <option value="">Модели не загружены</option>
                            ) : (
                                models.map((model) => (
                                    <option
                                        key={`${model.provider}:${model.model_name}`}
                                        value={`${model.provider}:${model.model_name}`}
                                    >
                                        {model.title} · {model.cost_credits} кр.
                                    </option>
                                ))
                            )}
                        </select>
                    </label>
                    <div className="model-details">
                        <span>Фото: до {selectedModel?.max_input_images ?? MAX_REFERENCE_IMAGES}</span>
                        <span>Цена фото: {selectedModel?.image_cost_credits ?? 0} кр.</span>
                    </div>
                </div>
                <div className="file-container">
                    <span className="file-title">Фото (опц.)</span>
                    <label className="file-selector">
                        <input
                            accept="image/png,image/jpeg,image/webp"
                            multiple
                            onChange={(event) => onFilesChange(event.target.files)}
                            ref={fileInputRef}
                            type="file"
                        />
                        <span className="upload-button">Выберите файл</span>
                        <span className="file-name">
                            {files.length > 0
                                ? files.map((file) => file.name).join(", ")
                                : "Файл не выбран"}
                        </span>
                    </label>
                </div>
                {error ? <div className="alert error-alert">{error}</div> : null}
                {notice ? <div className="alert notice-alert">{notice}</div> : null}
                <button
                    className="generate-btn btn"
                    disabled={isGenerating || isBootLoading}
                    type="submit"
                >
                    {isGenerating ? "Генерируем..." : "Сгенерировать"}
                </button>
            </form>
        </div>
    );
}