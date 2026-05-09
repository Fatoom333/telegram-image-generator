import type { UserResponse } from "../../api/types";
import CoinBtnIcon from "../../assets/coin_btn_icon.svg?react";
import AdminIcon from "../../assets/admin_icon.svg?react"

type Props = {
    user: UserResponse | null;
    isPaying: boolean;
    onPay: () => void;
};

export function HeaderActions({user, isPaying, onPay}: Props) {
    return (
        <div className="header-actions">
            <button className="pay-btn btn" disabled={isPaying} onClick={onPay} type="button">
                <CoinBtnIcon/>
                {isPaying ? "..." : "Пополнить"}
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