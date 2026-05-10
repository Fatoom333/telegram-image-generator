import type { PaymentProviderResponse, TariffResponse, UserResponse } from "../../api/types";
import { HeaderActions } from "./HeaderActions";
import { ProviderSelector } from "./ProviderSelector";
import { TariffSelector } from "./TariffSelector";

type Props = {
    user: UserResponse | null;
    loading: boolean;
    isPaying: boolean;
    onPay: () => void;
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onTariffSelect: (tariffId: string) => void;
    providers: PaymentProviderResponse[];
    selectedProvider: string;
    onProviderSelect: (providerId: string) => void;
};

export function HeaderAccount({
    user, 
    loading, 
    isPaying, 
    onPay, 
    tariffs, 
    selectedTariffId, 
    onTariffSelect, 
    providers, 
    selectedProvider, 
    onProviderSelect} : Props) {
    return (
        <div className="header-account-card header-card">
            <div className="account-info">
                <p>ID: <span className="bold">{user?.telegram_id ?? "-"}</span></p>
                <p>Имя: <span className="bold">{user?.first_name || user?.username || (loading ? "Загрузка..." : "Пользователь")}</span></p>
                <p>Баланс: <span className="bold">{user?.credits ?? "-"}</span></p>
            </div>
            <div className="account-actions">
                <TariffSelector
                    tariffs={tariffs}
                    selectedTariffId={selectedTariffId}
                    onTariffSelect={onTariffSelect}
                />
                <ProviderSelector
                    providers={providers}
                    selectedProvider={selectedProvider}
                    onProviderSelect={onProviderSelect}
                />
                <HeaderActions user={user} isPaying={isPaying} onPay={onPay}/>
            </div>
        </div>
    );
}