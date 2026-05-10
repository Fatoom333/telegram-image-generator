import type { ReactNode } from "react";
import DescIcon from "../assets/desc_icon.svg?react";
import { CardHeader } from "./misc/CardHeader";
import { useState } from "react";

type Props = {
    title: string;
    description: ReactNode;
};

export function AppDescription({title, description}: Props) {
    const [isOpen, setIsOpen] = useState(false);
    const toggle = () => setIsOpen((prev) => !prev);
    return(
        <div className="app-description-card card">
            <button
                type="button"
                onClick={toggle}
                className="app-description-card-toggle"
                aria-expanded={isOpen}
            >
            <CardHeader
                icon={<DescIcon/>}
                title={title}
            />
            <span className={`arrow ${isOpen ? "arrow--open" : ""}`}>▼</span>
            </button>
            {isOpen && <p className="app-description-content">{description}</p>}
        </div>
    );
}