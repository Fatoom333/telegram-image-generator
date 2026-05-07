type Props = {
    title: string;
    description: string;
};

export function EmptyStateIndicator({title, description}: Props) {
    return (
        <div className="empty-state-indicator">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
    );
}