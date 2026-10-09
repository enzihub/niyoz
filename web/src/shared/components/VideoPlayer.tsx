export const VideoPlayer = ({ src }: { src: string }) => {
  return (
    <div className='relative mb-8 mt-4 aspect-video w-full max-w-2xl overflow-hidden rounded-lg'>
      <iframe
        className='absolute left-0 top-0 h-full w-full'
        src={src}
        title='YouTube video player'
        allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
        allowFullScreen
      />
    </div>
  );
};
