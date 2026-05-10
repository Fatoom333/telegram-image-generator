import { HeaderBranding } from "./HeaderBranding";
import { HeaderAccount } from "./HeaderAccount";
import type { PaymentProviderResponse, TariffResponse, UserResponse } from "../../api/types";
import type { ReactNode } from "react";


type Props = {
    title: ReactNode;
    subtitle: string;
    logo: string;
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
            <HeaderAccount 
                user={user} 
                loading={loading}
                tariffs={tariffs}
                selectedTariffId={selectedTariffId}
                onTariffSelect={onTariffSelect}
                providers={providers}
                selectedProvider={selectedProvider}
                onProviderSelect={onProviderSelect}
                isPaying={isPaying}
                onPay={onPay}
            />
        </header>
    );
}
