import type { UserResponse } from "../../api/types";
import CoinBtnIcon from "../../assets/coin_btn_icon.svg?react";
import AdminIcon from "../../assets/admin_icon.svg?react"

type Props = {
    user: UserResponse | null;
    onOpenPaymentModal: () => void;
};

export function HeaderActions({user, onOpenPaymentModal}: Props) {
    return (
        <div className="header-actions">
            <button className="pay-btn btn" onClick={onOpenPaymentModal} type="button">
                <CoinBtnIcon/>
                Пополнить
            </button>
            { user?.is_admin === true && (
                <button 
                    className="admin-btn btn" 
                    onClick={() => {window.location.href = "/docs";}}
                    type="button"
                >
                    <AdminIcon/>
                    Админ
                </button>
            )}
          </div>
    );
}