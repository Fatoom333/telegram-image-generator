import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import {
	createGeneration,
	createPurchase,
	getBalance,
	getMe,
	listGenerations,
	listModels,
	listPaymentProviders,
	listTariffs,
} from "./api/api";
import type {
	AIModelResponse,
	GenerationResponse,
	PaymentProviderResponse,
	TariffResponse,
	UserResponse,
} from "./api/types";
import { MAX_REFERENCE_IMAGES, POLL_INTERVAL_MS } from "./misc/constants";
import { makeModelKey } from "./misc/make_model_key";
import { getErrorMessage } from "./misc/get_error_message";
import { BackgroundDecor } from "./components/misc/BackgroundDecor";
import { AppHeader } from "./components/header/AppHeader";
import { GenerationForm } from "./components/GenerationForm";
import { AppDescription } from "./components/AppDescription";
import { HistoryList } from "./components/history/HistoryList";
import logoUrl from "./assets/small_dark_logo.png";
import { PaymentModal } from "./components/PaymentModal";

export default function App() {
	const fileInputRef = useRef<HTMLInputElement | null>(null);
	const [user, setUser] = useState<UserResponse | null>(null);
	const [models, setModels] = useState<AIModelResponse[]>([]);
	const [selectedModelKey, setSelectedModelKey] = useState("");
	const [tariffs, setTariffs] = useState<TariffResponse[]>([]);
	const [_, setProviders] = useState<PaymentProviderResponse[]>([]);
	const [selectedTariffId, setSelectedTariffId] = useState("");
	const [selectedProvider, setSelectedProvider] = useState("");
	const [generations, setGenerations] = useState<GenerationResponse[]>([]);
	const [prompt, setPrompt] = useState("");
	const [files, setFiles] = useState<File[]>([]);
	const [isBootLoading, setIsBootLoading] = useState(true);
	const [isGenerating, setIsGenerating] = useState(false);
	const [isPaying, setIsPaying] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [notice, setNotice] = useState<string | null>(null);
	const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
	const [paymentError, setPaymentError] = useState<string | null>(null);
	const openPaymentModal = () => { setPaymentError(null); setIsPaymentModalOpen(true); }
	const closePaymentModal = () => { if(!isPaying) setIsPaymentModalOpen(false); };

	useEffect(() => {
		if (isPaymentModalOpen) { document.body.style.overflow = "hidden"; }
		else { document.body.style.overflow = ""; }
		return () => { document.body.style.overflow = ""; };
	}, [isPaymentModalOpen]);
	
	const selectedModel = useMemo(() => {
		return (
			models.find((model) => makeModelKey(model) === selectedModelKey) ?? null
		);
	}, [models, selectedModelKey]);
	
	async function bootstrap() {
		setIsBootLoading(true);
		setError(null);
		try {
			const [
				loadedModels,
				loadedTariffs,
				loadedProviders,
				loadedUser,
				loadedGenerations,
			] = await Promise.all([
				listModels(),
				listTariffs(),
				listPaymentProviders(),
				getMe(),
				listGenerations(),
			]);
			setModels(loadedModels);
			setTariffs(loadedTariffs);
			setProviders(loadedProviders);
			setUser(loadedUser);
			setGenerations(loadedGenerations);
			if (loadedModels.length > 0)
				setSelectedModelKey(makeModelKey(loadedModels[0]));
			if (loadedTariffs.length > 0) setSelectedTariffId(loadedTariffs[0].id);
			if (loadedProviders.length > 0)
				setSelectedProvider(loadedProviders[0].id);
		} catch (e) {
			setError(getErrorMessage(e));
		} finally {
			setIsBootLoading(false);
		}
	}
	
	useEffect(() => {
		window.Telegram?.WebApp?.ready?.();
		window.Telegram?.WebApp?.expand?.();
		void bootstrap();
	}, []);

	async function refreshUser() {
		const [nextUser, nextBalance] = await Promise.all([getMe(), getBalance()]);
		setUser({ ...nextUser, credits: nextBalance.credits });
	}
	
	async function refreshGenerations() {
		try {
			const next = await listGenerations();
			setGenerations(next);
		} catch (e) {
			setError(getErrorMessage(e));
		}
	}
	
	useEffect(() => {
		const hasActiveGeneration = generations.some((g) =>
			["created", "queued", "processing", "pending", "running"].includes(
			g.status.toLowerCase(),
		),
	);
	if (!hasActiveGeneration) return;
	const timerId = window.setInterval(() => {
		void refreshGenerations();
	}, POLL_INTERVAL_MS);
	return () => window.clearInterval(timerId);
}, [generations]);

function handleFilesChange(nextFiles: FileList | null) {
	setFiles(Array.from(nextFiles ?? []).slice(0, MAX_REFERENCE_IMAGES));
}

async function handleGenerate(e: FormEvent<HTMLFormElement>) {
	e.preventDefault();
	if (!prompt.trim()) {
		setError("Введите промпт перед генерацией.");
		return;
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
		setGenerations((prev) => [gen, ...prev]);
		setPrompt("");
		setFiles([]);
		if (fileInputRef.current) fileInputRef.current.value = "";
		await refreshUser();
		setNotice(
			"Генерация поставлена в очередь. История обновится автоматически.",
		);
	} catch (e) {
		setError(getErrorMessage(e));
	} finally {
		setIsGenerating(false);
	}
}

async function handlePay() {
	if (!selectedTariffId) {
		setPaymentError("Выберите тариф.");
		return;
	}
	if (!selectedProvider) {
		setPaymentError("Выберите способ оплаты.");
		return;
	}
	setIsPaying(true);
	setPaymentError(null);
	try {
		const purchase = await createPurchase(selectedTariffId, selectedProvider);
		if (purchase.payment_url) {
			window.Telegram?.WebApp?.openLink?.(purchase.payment_url);
			window.open(purchase.payment_url, "_blank", "noopener,noreferrer");
			setIsPaymentModalOpen(false);
			return;
		}
		setNotice(
			"Заявка на пополнение создана. Администратор начислит кредиты после проверки оплаты.",
		);
	} catch (e) {
		setPaymentError(getErrorMessage(e));
	} finally {
		setIsPaying(false);
	}
}

const infoDescription = (
	<>
	Пополните баланс, напишите промпт и прикрепите фото‑исходники по желанию.
	Нажмите кнопку <span className="bold">«Сгенерировать»</span> и дождитесь
	результата в истории генераций.<br/> Каждая генерация стоит{" "}
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
		user={user}
		loading={isBootLoading}
		onOpenPaymentModal={openPaymentModal}
	/>
	
	<AppDescription
		title="Как пользоваться?"
		description={infoDescription}
	/>
	
	<GenerationForm
		prompt={prompt}
		onPromptChange={setPrompt}
		models={models}
		selectedModelKey={selectedModelKey}
		onModelChange={setSelectedModelKey}
		selectedModel={selectedModel}
		files={files}
		onFilesChange={handleFilesChange}
		fileInputRef={fileInputRef}
		error={error}
		notice={notice}
		isGenerating={isGenerating}
		isBootLoading={isBootLoading}
		onSubmit={handleGenerate}
	/>

	<div className="history-card card">
		<HistoryList 
			generations={generations}
			isBootLoading={isBootLoading}
		/>
	</div>
	
	{isPaymentModalOpen && (
		<PaymentModal
			tariffs={tariffs}
			selectedTariffId={selectedTariffId}
        	onTariffSelect={setSelectedTariffId}
			error={paymentError}
        	isPaying={isPaying}
        	onPay={handlePay}
        	onClose={closePaymentModal}
		/>
	)}
	</main>
);
}
