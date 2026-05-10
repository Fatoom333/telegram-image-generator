import { HeaderBranding } from "./HeaderBranding";
import { HeaderAccount } from "./HeaderAccount";
import type { /* PaymentProviderResponse, TariffResponse, */ UserResponse } from "../../api/types";
import type { ReactNode } from "react";


type Props = {
    title: ReactNode;
    subtitle: string;
    logo: string;
    user: UserResponse | null;
    loading: boolean;
    onOpenPaymentModal: () => void;
};

export function AppHeader({
    title, 
    subtitle, 
    logo, 
    user, 
    loading,
    onOpenPaymentModal,
    /* 
    isPaying, 
    onPay, 
    tariffs, 
    selectedTariffId,
    onTariffSelect,
    providers,
    selectedProvider,
    onProviderSelect 
    */}: Props) {
    return (
        <header className="app-header card">
            <HeaderBranding title={title} subtitle={subtitle} logo={logo}/>
            <HeaderAccount 
                user={user} 
                loading={loading}
                onOpenPaymentModal={onOpenPaymentModal}
            />
        </header>
    );
}
