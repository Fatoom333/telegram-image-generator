type Props = {
    placeholderText: string;
    prompt: string;
    setPrompt: (value: string) => void;
    onSubmit: () => void;
    setFile: (file?: File | null) => void;
    loading: boolean;
};

export function GenerationForm({placeholderText, prompt, setPrompt, onSubmit, setFile, loading}: Props) {
    return (
        <div className="generation-form-card card">
            <div className="generation-form-textarea-container">
                <p><span className="bold-text">Новая генерация</span></p>
                <textarea 
                    className="generation-form-textarea" 
                    placeholder={placeholderText} 
                    value={prompt} 
                    onChange={(e) => setPrompt(e.target.value)} 
                />
            </div>
            <div className="generation-form-file-input-container">
                <p><span className="bold-text">Фото (опц.)</span></p>
                {/* add code for multiple file choices later*/}
                <input className="generation-form-file-input" type="file" accept=".jpg,.jpeg,.png,.webp" onChange={(e) => setFile(e.target.files?.[0])}/>
            </div>
            <button className="generation-form-submit-button" onClick={onSubmit} disabled={loading}>
                {loading ? "Генерируем..." : "Сгенерировать"}
            </button>
        </div>
    );
}