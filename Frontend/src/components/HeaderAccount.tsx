import type { MeResponse } from "../api/types";
import default_account_icon from "../assets/default_account_icon.png";

type Props = {
    me?: MeResponse | null;
    loading: boolean;
    onReplenishBalance: () => void;
};

export function HeaderAccount({me, loading, onReplenishBalance} : Props) {
    const id = me?.id ?? 1;
    const name = me?.username ?? me?.firstName ?? "Пользователь";
    const balance = me?.balance ?? 0;
    return (
        <div className="header-account-card header-card">
            <div className="header-account-info">
                <div className="header-account-fields">
                    <p>ID: {id}</p>
                    <p>Имя: {name}</p>
                    <p>Баланс: {balance}</p>
                </div>
                <img className="header-account-icon" src={default_account_icon} alt="Account icon"/>
            </div>
            <button className="header-account-replenish-button" onClick={onReplenishBalance} disabled={loading}>
                {loading ? "Пополнение..." : "Пополнить"}
            </button>
        </div>
    );
}