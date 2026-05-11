import { useNavigate } from "react-router";
import { useAppContext } from "../App";
import { PaymentModal } from "../components/PaymentModal";

export function PaymentPage() {
    const context = useAppContext();
    const navigate = useNavigate();
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