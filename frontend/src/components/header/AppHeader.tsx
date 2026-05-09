import { HeaderBranding } from "./HeaderBranding";
import { HeaderAccount } from "./HeaderAccount";
import { HeaderActions } from "./HeaderActions";
import type { PaymentProviderResponse, TariffResponse, UserResponse } from "../../api/types";
import type { ReactNode } from "react";
import { TariffSelector } from "./TariffSelector";
import { ProviderSelector } from "./ProviderSelector";

type Props = {
    title: ReactNode;
    subtitle: string;
    logo: string;
    user: UserResponse | null;
    loading: boolean;
    isPaying: boolean;
    onPay(): () => void;
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onTariffSelect: (tariffId: string) => void;
    providers: PaymentProviderResponse[];
    selectedProvider: string;
    onProviderSelect: (providerId: string) => void;
};

export function AppHeader({
    title, 
    subtitle, 
    logo, 
    user, 
    loading, 
    isPaying, 
    onPay, 
    tariffs, 
    selectedTariffId,
    onTariffSelect,
    providers,
    selectedProvider,
    onProviderSelect }: Props) {
    return (
        <header className="app-header card">
            <HeaderBranding title={title} subtitle={subtitle} logo={logo}/>
            <div className="header-account-card">
                <HeaderAccount user={user} loading={loading}/>
                <TariffSelector
                    tariffs={tariffs}
                    selectedTariffId={selectedTariffId}
                    onSelect={onTariffSelect}
                />
                <ProviderSelector
                    providers={providers}
                    selectedProvider={selectedProvider}
                    onSelect={onProviderSelect}
                />
                <HeaderActions user={user} isPaying={isPaying} onPay={onPay}/>
            </div>
        </header>
    );
}
