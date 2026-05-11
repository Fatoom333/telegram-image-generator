import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { createGeneration } from "../api/api";
import { MAX_REFERENCE_IMAGES, POLL_INTERVAL_MS } from "../misc/constants";
import { makeModelKey } from "../misc/make_model_key";
import { getErrorMessage } from "../misc/get_error_message";
import { useAppContext } from "../App";
import { BackgroundDecor } from "../components/misc/BackgroundDecor";
import { AppHeader } from "../components/header/AppHeader";
import { GenerationForm } from "../components/GenerationForm";
import { AppDescription } from "../components/AppDescription";
import { HistoryList } from "../components/history/HistoryList";
import logoUrl from "../assets/small_dark_logo.png"

export function MainPage() {
    const context = useAppContext();
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [selectedModelKey, setSelectedModelKey] = useState("");
    const [prompt, setPrompt] = useState("");
    const [files, setFiles] = useState<File[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [notice, setNotice] = useState<string | null>(null);

    useEffect(() => {
        if (context.models.length > 0 && !selectedModelKey) {
            setSelectedModelKey(makeModelKey(context.models[0]));
        }
    }, [context.models, selectedModelKey]);

    const selectedModel = useMemo(() => {
        return context.models.find((m) => makeModelKey(m) === selectedModelKey) ?? null;
    }, [context.models, selectedModelKey]);

    useEffect(() => {
        const hasActive = context.generations.some((g) =>
            ["created", "queued", "processing", "pending", "running"].includes(g.status.toLowerCase()));
        if (!hasActive) return;
        const id = window.setInterval(() => {
            void context.refreshGenerations();
        }, POLL_INTERVAL_MS);
        return () => window.clearInterval(id);
    }, [context.generations, context.refreshGenerations]);

    function handleFilesChange(nextFiles: FileList | null) {
        setFiles(Array.from(nextFiles ?? []).slice(0, MAX_REFERENCE_IMAGES));
    }

    async function handleGenerate(e: FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if(!prompt.trim()) {
            setError("Введите промпт перед генерацией");
        }
        setIsGenerating(true);
        setError(null);
        setNotice(null);
        try {
            const gen = await createGeneration({
                prompt,
                provider: selectedModel?.provider,
                modelName: selectedModel?.model_name,
                images: files,
            });
            context.addGeneration(gen);
            setPrompt("");
            setFiles([]);
            if (fileInputRef.current) fileInputRef.current.value = "";
            await context.refreshUser();
            setNotice("Генерация поставлена в очередь. История обновится автоматически.");
        } catch (e) {
            setError(getErrorMessage(e));
        } finally {
            setIsGenerating(false);
        }
    };

    const infoDescription = (
        <>
        Пополните баланс, напишите промпт и прикрепите фото‑исходники по желанию.
        Нажмите кнопку <span className="bold">«Сгенерировать»</span> и дождитесь
        результата в истории генераций.<br /> Каждая генерация стоит{" "}
        <span className="bold">{selectedModel?.cost_credits ?? 10} кредитов</span>
        . Баланс можно пополнить в любое время, нажав кнопку «Пополнить».
        </>
    );
    return (
        <main className="app-shell">
            <BackgroundDecor />

            <AppHeader
                title={<>Neiro<span>Banana</span></>}
                subtitle="Генерация фото и видео на базе NanoBanana!"
                logo={logoUrl}
                user={context.user}
                loading={context.isBootLoading}
                onOpenPaymentModal={() => navigate("/payments")}
            />

            <AppDescription title="Как пользоваться?" description={infoDescription} />

            <GenerationForm
                prompt={prompt}
                onPromptChange={setPrompt}
                models={context.models}
                selectedModelKey={selectedModelKey}
                onModelChange={setSelectedModelKey}
                selectedModel={selectedModel}
                files={files}
                onFilesChange={handleFilesChange}
                fileInputRef={fileInputRef}
                error={error}
                notice={notice}
                isGenerating={isGenerating}
                isBootLoading={context.isBootLoading}
                onSubmit={handleGenerate}
            />

            <div className="history-card card">
                <HistoryList generations={context.generations} isBootLoading={context.isBootLoading} />
            </div>
        </main>
    );
}