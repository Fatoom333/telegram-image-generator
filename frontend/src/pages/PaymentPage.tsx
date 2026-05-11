import { useNavigate } from "react-router";
import { useAppContext } from "../App";
import { PaymentModal } from "../components/PaymentModal";
import { useEffect } from "react";

export function PaymentPage() {
    const context = useAppContext();
    const navigate = useNavigate();
    useEffect(() => {
        const backBtn = window.Telegram?.WebApp?.BackButton;
        if (!backBtn) return;
        backBtn.show();
        const handleBack = () => navigate("/");
        return () => {
            backBtn.offClick(handleBack);
            backBtn.hide()
        }
    }, [navigate]);
    return (
        <PaymentModal
            tariffs={context.tariffs}
            selectedTariffId={context.selectedTariffId}
            onTariffSelect={context.setSelectedTariffId}
            isPaying={context.isPaying}
            onPay={context.handlePay}
            onClose={() => navigate("/")}
            error={context.paymentError}
        />
    );
}