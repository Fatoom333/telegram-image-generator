import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { BrowserRouter, Routes, Route } from "react-router";
import {
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
import { getErrorMessage } from "./misc/get_error_message";
import { MainPage } from "./pages/MainPage"
import { PaymentPage } from "./pages/PaymentPage";

export interface AppContextValue {
	user: UserResponse | null;
  	models: AIModelResponse[];
  	tariffs: TariffResponse[];
  	providers: PaymentProviderResponse[];
  	selectedTariffId: string;
  	setSelectedTariffId: (id: string) => void;
  	selectedProvider: string;
  	setSelectedProvider: (id: string) => void;
  	generations: GenerationResponse[];
  	addGeneration: (gen: GenerationResponse) => void;
  	refreshGenerations: () => Promise<void>;
  	refreshUser: () => Promise<void>;
  	isBootLoading: boolean;
  	paymentError: string | null;
  	setPaymentError: (err: string | null) => void;
  	isPaying: boolean;
  	setIsPaying: (paying: boolean) => void;
  	handlePay: () => Promise<void>;
}

const AppContext = createContext<AppContextValue | null>(null);

export function useAppContext(): AppContextValue {
	const context = useContext(AppContext);
	if(!context) throw new Error();
	return context;
}

function AppProvider() {
	const [user, setUser] = useState<UserResponse | null>(null);
	const [models, setModels] = useState<AIModelResponse[]>([]);
	const [tariffs, setTariffs] = useState<TariffResponse[]>([]);
	const [providers, setProviders] = useState<PaymentProviderResponse[]>([]);
	const [selectedTariffId, setSelectedTariffId] = useState("");
	const [selectedProvider, setSelectedProvider] = useState("");
	const [generations, setGenerations] = useState<GenerationResponse[]>([]);
	const [isBootLoading, setIsBootLoading] = useState(true);
	const [isPaying, setIsPaying] = useState(false);
	const [paymentError, setPaymentError] = useState<string | null>(null);
	
	const addGeneration = useCallback((gen: GenerationResponse) => {
		setGenerations((prev) => [gen, ...prev]);
	},[]);
	const refreshUser = useCallback(async () => {
		const [nextUser, nextBalance] = await Promise.all([getMe(), getBalance()]);
		setUser({...nextUser, credits: nextBalance.credits});
	}, []);
	const refreshGenerations = useCallback(async () => {
		const next = await listGenerations();
		setGenerations(next);
	}, []);

	useEffect(() => {
		async function bootstrap() {
			setIsBootLoading(true);
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
			if (loadedTariffs.length > 0) setSelectedTariffId(loadedTariffs[0].id);
			if (loadedProviders.length > 0) setSelectedProvider(loadedProviders[0].id);
			} catch (e) {
				console.error(getErrorMessage(e));
			} finally {
				setIsBootLoading(false);
			}	
		}
		window.Telegram?.WebApp?.ready?.();
		window.Telegram?.WebApp?.expand?.();
		void bootstrap();
	}, []);
	const handlePay = useCallback(async () => {
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
				return;
			}
		} catch (e) {
			setPaymentError(getErrorMessage(e));
		} finally {
			setIsPaying(false);
		}
	}, [selectedTariffId, selectedProvider]);

	const contextValue: AppContextValue = {
    	user,
    	models,
    	tariffs,
    	providers,
    	selectedTariffId,
    	setSelectedTariffId,
    	selectedProvider,
    	setSelectedProvider,
    	generations,
    	addGeneration,
    	refreshGenerations,
    	refreshUser,
    	isBootLoading,
    	paymentError,
    	setPaymentError,
    	isPaying,
    	setIsPaying,
    	handlePay,
  	};
	return (
		<AppContext.Provider value={contextValue}>
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<MainPage/>}/>
					<Route path="/payments" element={<PaymentPage/>}/>
				</Routes>
			</BrowserRouter>
		</AppContext.Provider>
	);
}

export default function App() {
	return <AppProvider/>;
}