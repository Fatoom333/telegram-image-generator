import { useState, useCallback, useEffect, useMemo } from 'react';
import { retrieveLaunchParams, postEvent } from '@tma.js/sdk';
import { getMe, getGenerations, getTariffs, postPurchase, postGeneration } from './api/api.ts';
import type { MeResponse, GenerationResponse } from './api/types';
import { AppHeader } from './components/AppHeader.tsx';
import { AppDescription } from './components/AppDescription.tsx';
import { GenerationForm } from './components/GenerationForm.tsx';
import { HistoryModule } from './components/HistoryModule.tsx';

interface TelegramWebApp {
    WebApp?: {
        openInvoice: (url: string, callback: (status: string) => void) => void;
    };
}

export default function App() {
    const lp = retrieveLaunchParams();
    const token = useMemo(() => lp.initDataRaw as string, [lp.initDataRaw]);
    const [me, setMe] = useState<MeResponse | null>(null);
    const [generations, setGenerations] = useState<GenerationResponse[]>([]);
    const [prompt, setPrompt] = useState('');
    const [fileState, setFileState] = useState<File | null>(null);
    const [loadingReplenish, setLoadingReplenish] = useState(false);
    const [loadingGenerate, setLoadingGenerate] = useState(false);
    const [error, setError] = useState<string | null>(!token ? 'Not telegram environment' : null);
    const [formKey, setFormKey] = useState(0);

    const setFile = (file?: File | null) => setFileState(file ?? null);

    const showError = useCallback((msg: string) => {
        setError(msg);
        const timer = setTimeout(() => setError(null), 6000);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (!token) {
            return;
        }
        const fetchInitData = async () => {
            try {
                const [meData, gensData] = await Promise.all([
                    getMe(token),
                    getGenerations(token, 100, 0)
                ]);
                setMe(meData);
                setGenerations(gensData);
            } catch (err: unknown) {
                const msg = err instanceof Error ? err.message : 'Can not get generations list';
                showError(msg);
            }
        };
        fetchInitData();
    }, [token, showError]);
    
    const handleReplenishBalance = useCallback(async () => {
        setLoadingReplenish(true);
        try {
            const tariffs = await getTariffs();
            if (!tariffs.length) throw new Error('No current tariffs');
            const tariff = tariffs[0]; // add selection later
            const purchase = await postPurchase(token, {tariff_id: tariff.id});
            if (!purchase.payment_url) throw new Error('Payment link has not been received');
            const invoiceUrl = purchase.payment_url;
            try {
                postEvent('web_app_open_invoice', {slug: invoiceUrl});
            } catch {
                const w = window as unknown as { Telegram?: TelegramWebApp };
                if (typeof window !== 'undefined' && w.Telegram?.WebApp?.openInvoice) {
                    w.Telegram.WebApp.openInvoice(invoiceUrl, (status: string) => {
                        if (status === 'paid') {
                            getMe(token).then(setMe).catch(console.error);
                        }
                    });
                } else {
                    window.open(invoiceUrl, '_blank');
                }
            }
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Could not replenish balance';
            showError(msg);
        } finally {
            setLoadingReplenish(false);
        }
    }, [token, showError]);

    const handleGenerate = useCallback(async () => {
        if (!prompt.trim()) {
            showError('Prompt needed to create a generation');
            return;
        }

        setLoadingGenerate(true);
        try {
            let images: string[] | null = null;
            if (fileState) {
                const b = await new Promise<string>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result as string);
                    reader.onerror = reject;
                    reader.readAsDataURL(fileState);
                });
                images = [b];
            }
            const newGeneration = await postGeneration(token, {prompt, images});
            setGenerations((prev) => [newGeneration, ...prev]);
            setPrompt('');
            setFileState(null);
            setFormKey((k) => k + 1);
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Could not create a generation';
            showError(msg);
        } finally {
            setLoadingGenerate(false);
        }
    }, [prompt, fileState, token, showError]);
    return (
        <div className='app'>
            <div className='container'>
                <div className='stack'>
                    <AppHeader
                        title="NeiroBanano"
                        subtitle="Генерация фото/видео на базе NanoBanana!"
                        me={me}
                        loading={loadingReplenish}
                        onReplenishBalance={handleReplenishBalance}
                    />

                    <AppDescription
                        intro="Как пользоваться?"
                        description="Опиши, что хочешь сгенерировать, прикрепи по необходимости изображения-референсы и жми кнопку «Сгенерировать»!<br>Для новых пользователей n кредитов бесплатно!"
                    />

                    <GenerationForm
                        key={formKey}
                        placeholderText="Акула в шляпе танцет танго..."
                        prompt={prompt}
                        setPrompt={setPrompt}
                        onSubmit={handleGenerate}
                        setFile={setFile}
                        loading={loadingGenerate}
                    />

                    <HistoryModule
                        generations={generations}
                    />
                </div>
            </div>
            {error && (
                <div className='error-card' onClick={() => setError(null)} role="alert">{error}</div>
            )}
        </div>
    );
}