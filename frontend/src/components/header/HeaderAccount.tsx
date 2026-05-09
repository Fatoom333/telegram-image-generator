import type { UserResponse } from "../../api/types";

type Props = {
    user: UserResponse | null;
    loading: boolean;
};

export function HeaderAccount({user, loading} : Props) {
    return (
        <div className="header-account-card header-card">
            <p>ID: {user?.telegram_id ?? "-"}</p>
            <p>Имя: {user?.first_name || user?.username || (loading ? "Загрузка..." : "Пользователь")}</p>
            <p>Баланс: {user?.credits ?? "-"}</p>
        </div>
    );
}