import type { ReactNode } from "react";
import DescIcon from "../assets/desc_icon.svg?react";
import { CardHeader } from "./misc/CardHeader";

type Props = {
    title: string;
    description: ReactNode;
};

export function AppDescription({title, description}: Props) {
    return(
        <div className="app-description-card card">
            <CardHeader
                icon={<DescIcon/>}
                title={title}
            />
            <p>{description}</p>
        </div>
    );
}