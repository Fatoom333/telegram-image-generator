import type { MeResponse } from "../api/types";

type Props = {
    me?: MeResponse | null;
    loading: boolean;
    onReplenishBalance: () => void;
};

export function HeaderAccount({me, loading, onReplenishBalance} : Props) {
    const id = me?.telegram_id ?? 1;
    const name = me?.username ?? me?.first_name ?? "Пользователь";
    const balance = me?.credits ?? 0;
    return (
        <div className="header-account-card header-card">
            <div className="header-account-container">
                <div className="header-account-info">
                    <p><span className="bold-text">ID: </span>{id}</p>
                    <p><span className="bold-text">Имя: </span>{name}</p>
                    <p><span className="bold-text">Баланс: </span>{balance}</p>
                </div>
                <button className="header-account-replenish-button" onClick={onReplenishBalance} disabled={loading}>
                    {loading ? "Пополнение..." : "Пополнить"}
                </button>
            </div>
        </div>
    );
}