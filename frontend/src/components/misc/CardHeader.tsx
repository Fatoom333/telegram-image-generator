import type { ReactNode } from "react"

type Props = {
    icon: ReactNode;
    title: string;
};

export function CardHeader({icon, title}: Props) {
    return (
        <div className="card-header">
            {icon}
            <div className="card-header-title">
                <h2>{title}</h2>
                <hr className="line"/>
            </div>
        </div>
    );
}