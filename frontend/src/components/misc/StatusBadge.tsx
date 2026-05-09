type Props = {
    status: string;
};

export function StatusBadge({status}: Props) {
    const statusTexts: Record<string, string> = {
        created: "Создано",
        queued: "В очереди",
        running: "Генерируется",
        processing: "Генерируется",
        pending: "В очереди",
        succeeded: "Готово",
        completed: "Готово",
        failed: "Ошибка",
        canceled: "Отменено"
    };
    const tmp = status?.toLowerCase() ?? "";
    return (
        <span className={`status-badge status-${tmp}`}>{statusTexts[tmp] ?? status}</span>
    );
}