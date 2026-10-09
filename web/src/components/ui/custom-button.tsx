export default function CustomButton({
  buttonText,
  width,
  className,
  onClick,
  disabled,
  icon,
}: {
  buttonText: string;
  width?: string;
  className?: string;
  disabled?: boolean;
  icon?: JSX.Element;
  onClick?: () => void;
}) {
  return (
    <button
      className={`mx-auto flex items-center justify-center gap-2.5 rounded-2xl shadow-lg transition-all duration-300 ease-in-out hover:scale-[1.02] hover:shadow-lg hover:brightness-110 ${width} ${className} `}
      onClick={onClick}
      disabled={disabled}
    >
      {buttonText} {icon}
    </button>
  );
}
