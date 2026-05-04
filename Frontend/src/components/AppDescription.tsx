type Props = {
    intro: string;
    description: string;
};

export function AppDescription({intro, description}: Props) {
    return(
        <div className="app-description-card card">
            <h1>{intro}</h1>
            <p>{description}</p>
        </div>
    );
}