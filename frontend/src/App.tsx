import { useEffect, useMemo, useRef, useState } from "react";
import logoUrl from "./assets/small_dark_logo.png";
import type { FormEvent } from "react";
import {
  absoluteApiUrl,
  createGeneration,
  createPurchase,
  getBalance,
  getMe,
  listGenerations,
  listModels,
  listTariffs,
} from "./api/api";
import type {
  AIModelResponse,
  GenerationResponse,
  TariffResponse,
  UserResponse,
} from "./api/types";
import "./index.css";

const MAX_REFERENCE_IMAGES = 2;
const POLL_INTERVAL_MS = 4000;

function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [user, setUser] = useState<UserResponse | null>(null);
  const [models, setModels] = useState<AIModelResponse[]>([]);
  const [selectedModelKey, setSelectedModelKey] = useState("");
  const [tariffs, setTariffs] = useState<TariffResponse[]>([]);
  const [generations, setGenerations] = useState<GenerationResponse[]>([]);
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [isBootLoading, setIsBootLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPaying, setIsPaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const selectedModel = useMemo(() => {
    return models.find((model) => makeModelKey(model) === selectedModelKey) ?? null;
  }, [models, selectedModelKey]);

  const activeTariff = useMemo(() => {
    return tariffs[0] ?? null;
  }, [tariffs]);

  useEffect(() => {
    window.Telegram?.WebApp?.ready?.();
    window.Telegram?.WebApp?.expand?.();

    void bootstrap();
  }, []);

  useEffect(() => {
    const hasActiveGeneration = generations.some((generation) => {
      return ["queued", "processing", "pending", "running"].includes(generation.status.toLowerCase());
    });

    if (!hasActiveGeneration) {
      return undefined;
    }

    const timerId = window.setInterval(() => {
      void refreshGenerations();
    }, POLL_INTERVAL_MS);

    return () => {
      window.clearInterval(timerId);
    };
  }, [generations]);

  async function bootstrap() {
    setIsBootLoading(true);
    setError(null);

    try {
      const [loadedModels, loadedTariffs, loadedUser, loadedGenerations] = await Promise.all([
        listModels(),
        listTariffs(),
        getMe(),
        listGenerations(),
      ]);

      setModels(loadedModels);
      setTariffs(loadedTariffs);
      setUser(loadedUser);
      setGenerations(loadedGenerations);

      if (loadedModels.length > 0) {
        setSelectedModelKey(makeModelKey(loadedModels[0]));
      }
    } catch (apiError) {
      setError(getErrorMessage(apiError));
    } finally {
      setIsBootLoading(false);
    }
  }

  async function refreshUser() {
    const [nextUser, nextBalance] = await Promise.all([getMe(), getBalance()]);

    setUser({
      ...nextUser,
      credits: nextBalance.credits,
    });
  }

  async function refreshGenerations() {
    try {
      const nextGenerations = await listGenerations();
      setGenerations(nextGenerations);
    } catch (apiError) {
      setError(getErrorMessage(apiError));
    }
  }

  function handleFilesChange(nextFiles: FileList | null) {
    const pickedFiles = Array.from(nextFiles ?? []).slice(0, MAX_REFERENCE_IMAGES);

    setFiles(pickedFiles);
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!prompt.trim()) {
      setError("Введите промпт перед генерацией.");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setNotice(null);

    try {
      const generation = await createGeneration({
        prompt,
        provider: selectedModel?.provider,
        modelName: selectedModel?.model_name,
        images: files,
      });

      setGenerations((currentGenerations) => [generation, ...currentGenerations]);
      setPrompt("");
      setFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await refreshUser();

      setNotice("Генерация поставлена в очередь. История обновится автоматически.");
    } catch (apiError) {
      setError(getErrorMessage(apiError));
    } finally {
      setIsGenerating(false);
    }
  }

  async function handlePay() {
    if (!activeTariff) {
      setError("Тарифы пока не настроены.");
      return;
    }

    setIsPaying(true);
    setError(null);

    try {
      const purchase = await createPurchase(activeTariff.id);

      if (purchase.payment_url) {
        window.Telegram?.WebApp?.openLink?.(purchase.payment_url);
        window.open(purchase.payment_url, "_blank", "noopener,noreferrer");
        return;
      }

      setNotice("Покупка создана, но payment_url не вернулся от backend.");
    } catch (apiError) {
      setError(getErrorMessage(apiError));
    } finally {
      setIsPaying(false);
    }
  }

  return (
    <main className="app-shell">
      <BackgroundDecor />

      <section className="hero-card">
  <div className="brand">
    <div className="logo-mark" aria-hidden="true">
      <img src={logoUrl} alt="NeiroBanana" />
    </div>

    <div className="brand-copy">
      <h1>
        Neiro<span>Banana</span>
      </h1>
      <p>Генерация фото и видео на базе NanoBanana!</p>
    </div>
  </div>

  <aside className="profile-card">
    <div className="profile-info">
      <p>ID: {user?.telegram_id ?? "—"}</p>
      <p>
        Имя:{" "}
        <strong>
          {user?.first_name || user?.username || (isBootLoading ? "Загрузка..." : "Пользователь")}
        </strong>
      </p>
      <p>
        Баланс: <strong>{user?.credits ?? "—"}</strong>
      </p>
    </div>

    <div className="profile-actions">
      <button className="gold-button compact" disabled={isPaying} onClick={handlePay} type="button">
        <span>▣</span>
        {isPaying ? "..." : "Пополнить"}
      </button>

      <button
        className="gold-button compact"
        onClick={() => {
          window.location.href = "/docs";
        }}
        type="button"
      >
        <span>♛</span>
        Админ
      </button>
    </div>
  </aside>
</section>

      <section className="glass-panel info-panel">
        <SectionHeading icon="?" title="Как пользоваться?" />

        <div className="divider" />

        <p>
          Пополните баланс, напишите промпт и прикрепите фото-исходники по желанию. Нажмите кнопку{" "}
          <mark>«Сгенерировать»</mark> и дождитесь результата в истории генераций.
        </p>
        <p>
          Каждая генерация стоит <mark>{selectedModel?.cost_credits ?? 10} кредитов</mark>. Баланс можно пополнить в
          любое время, нажав кнопку <mark>«Пополнить»</mark> справа вверху приложения.
        </p>

        <div className="info-illustration" aria-hidden="true">
          <div className="paper-icon">✎</div>
        </div>
      </section>

      <section className="glass-panel generation-panel">
        <SectionHeading icon="✦" title="Новая генерация" />

        <form onSubmit={handleGenerate}>
          <label className="sr-only" htmlFor="prompt">
            Промпт
          </label>

          <textarea
            id="prompt"
            maxLength={2000}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Введите промпт... (Например: Акула танцует танго)"
            value={prompt}
          />

          <div className="form-grid">
            <label className="field-label">
              Модель
              <select
                onChange={(event) => setSelectedModelKey(event.target.value)}
                value={selectedModelKey}
              >
                {models.length === 0 ? (
                  <option value="">Модели не загружены</option>
                ) : (
                  models.map((model) => (
                    <option key={makeModelKey(model)} value={makeModelKey(model)}>
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

          <div className="file-zone">
            <span className="file-title">Фото (опц.)</span>

            <label className="file-picker">
              <input
                accept="image/png,image/jpeg,image/webp"
                multiple
                onChange={(event) => handleFilesChange(event.target.files)}
                ref={fileInputRef}
                type="file"
              />

              <span className="upload-button">↥ Выберите файл</span>
              <span className="file-name">
                {files.length > 0 ? files.map((file) => file.name).join(", ") : "Файл не выбран"}
              </span>
            </label>
          </div>

          {error ? <div className="alert error-alert">{error}</div> : null}
          {notice ? <div className="alert notice-alert">{notice}</div> : null}

          <button className="gold-button generate-button" disabled={isGenerating || isBootLoading} type="submit">
            <span>✦</span>
            {isGenerating ? "Генерируем..." : "Сгенерировать"}
          </button>
        </form>
      </section>

      <section className="glass-panel history-panel">
        <SectionHeading icon="◷" title="История" />

        {generations.length === 0 ? (
          <div className="empty-state">
            <div className="folder-icon">✦</div>
            <h2>{isBootLoading ? "Загружаем историю..." : "Пока нет генераций"}</h2>
            <p>Самое время это исправить!</p>
          </div>
        ) : (
          <div className="history-list">
            {generations.map((generation) => (
              <GenerationCard key={generation.id} generation={generation} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function GenerationCard({ generation }: { generation: GenerationResponse }) {
  const outputImages = generation.images.filter((image) => image.role !== "input");

  return (
    <article className="generation-card">
      <div className="generation-meta">
        <div>
          <h3>{generation.prompt}</h3>
          <p>
            {generation.provider ?? "provider"} / {generation.model_name ?? "model"} ·{" "}
            {formatDate(generation.created_at)}
          </p>
        </div>

        <StatusBadge status={generation.status} />
      </div>

      {generation.error_message ? <p className="generation-error">{generation.error_message}</p> : null}

      {outputImages.length > 0 ? (
        <div className="image-grid">
          {outputImages.map((image) => (
            <a
              href={image.file_url ? absoluteApiUrl(image.file_url) : "#"}
              key={image.id}
              rel="noreferrer"
              target="_blank"
            >
              {image.file_url ? <AuthImage alt={generation.prompt} src={image.file_url} /> : null}
            </a>
          ))}
        </div>
      ) : (
        <p className="generation-wait">Результат появится здесь после обработки.</p>
      )}
    </article>
  );
}

function AuthImage({ src, alt }: { src: string; alt: string }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [isFailed, setIsFailed] = useState(false);

  useEffect(() => {
    let isCancelled = false;
    let createdUrl: string | null = null;

    async function loadImage() {
      setIsFailed(false);

      try {
        const headers = new Headers();
        const initData = window.Telegram?.WebApp?.initData ?? "";

        if (initData) {
          headers.set("X-Telegram-Init-Data", initData);
        }

        const response = await fetch(absoluteApiUrl(src), {
          headers,
        });

        if (!response.ok) {
          throw new Error(`Image load failed: ${response.status}`);
        }

        const blob = await response.blob();
        createdUrl = URL.createObjectURL(blob);

        if (!isCancelled) {
          setObjectUrl(createdUrl);
        }
      } catch {
        if (!isCancelled) {
          setIsFailed(true);
        }
      }
    }

    void loadImage();

    return () => {
      isCancelled = true;

      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
      }
    };
  }, [src]);

  if (isFailed) {
    return <div className="image-placeholder">Не удалось загрузить изображение</div>;
  }

  if (!objectUrl) {
    return <div className="image-placeholder">Загрузка...</div>;
  }

  return <img alt={alt} src={objectUrl} />;
}

function StatusBadge({ status }: { status: string }) {
  const normalizedStatus = status.toLowerCase();

  const labelByStatus: Record<string, string> = {
    created: "Создано",
    queued: "В очереди",
    running: "Генерируется",
    processing: "Генерируется",
    pending: "В очереди",
    succeeded: "Готово",
    completed: "Готово",
    failed: "Ошибка",
    canceled: "Отменено",
  };

  const label = labelByStatus[normalizedStatus] ?? status;

  return <span className={`status-badge status-${normalizedStatus}`}>{label}</span>;
}

function SectionHeading({ icon, title }: { icon: string; title: string }) {
  return (
    <header className="section-heading">
      <span>{icon}</span>
      <h2>{title}</h2>
    </header>
  );
}

function BackgroundDecor() {
  return (
    <div aria-hidden="true" className="background-decor">
      <span />
      <span />
      <span />
    </div>
  );
}

function makeModelKey(model: AIModelResponse): string {
  return `${model.provider}:${model.model_name}`;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    month: "2-digit",
  }).format(new Date(value));
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Неизвестная ошибка";
}

export default App;
