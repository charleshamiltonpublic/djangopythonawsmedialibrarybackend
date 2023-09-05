from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from .serializers import MediaFileSerializer
from .forms import MediaFileForm, RegistrationForm
from .models import MediaFile
from django.contrib.auth.decorators import login_required
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q

TAGS = {tag: value for tag, value in ExifTags.TAGS.items()}

def determine_file_type(filename):
    image_exts = ['jpg', 'jpeg', 'png', 'gif']
    video_exts = ['mp4', 'mkv', 'avi']
    # ... add more as necessary

    extension = filename.rsplit('.', 1)[1].lower()
    if extension in image_exts:
        return 'image'
    elif extension in video_exts:
        return 'video'
    # ... handle more types
    else:
        return 'unknown'

def create_thumbnail(input_image, base_width):
    img = Image.open(input_image)
    w_percent = base_width / float(img.width)
    h_size = int(float(img.height) * float(w_percent))
    img = img.resize((base_width, h_size), Image.LANCZOS)
    return img
def extract_metadata(image):
    metadata = {}
    try:
        info = image._getexif()
        if info is not None:
            for tag, value in info.items():
                tagname = TAGS.get(tag, tag)
                metadata[tagname] = value
    except (AttributeError, KeyError, IndexError):
        # cases: image doesn't have getexif
        pass
    return metadata


@login_required
def upload_media(request):
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES)
        print("Received request in upload_media.")
        if form.is_valid():
            print("Form is valid.")
            media = form.save(commit=False)
            media.user = request.user #put back when ready for user authentication
            media.filetype = determine_file_type(media.file.name)
            if media.filetype == 'image':
                image = Image.open(media.file)
                media.metadata = extract_metadata(image)
                thumbnail = create_thumbnail(media.file, 300)  # e.g., 300 pixels wide
                thumb_io = BytesIO()
                thumbnail.save(thumb_io, format='JPEG')
                media.thumbnail.save(f"thumb_{media.file.name}", ContentFile(thumb_io.getvalue()), save=False)
            media.save()
            return redirect('media_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = MediaFileForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def media_dashboard(request):
    # Initialize with user-specific media files
    media_files = MediaFile.objects.filter(user=request.user)

    query = request.GET.get('q')
    if query:
        media_files = media_files.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(metadata__your_metadata_field__icontains=query)
        )

    # Sorting
    sort_by = request.GET.get('sort_by')
    if sort_by:
        media_files = media_files.order_by(sort_by)
    
    # Filtering by file type
    file_type = request.GET.get('file_type')
    if file_type:
        media_files = media_files.filter(filetype=file_type)
    
    # Filtering by tags
    tag = request.GET.get('tag')
    if tag:
        media_files = media_files.filter(tags__name__in=[tag])
        
    return render(request, 'media_dashboard.html', {'media_files': media_files})


@login_required
def edit_media(request, media_id):
    media = get_object_or_404(MediaFile, id=media_id, user=request.user)

@login_required
def delete_media(request, media_id):
    media = get_object_or_404(MediaFile, id=media_id, user=request.user)
    media.delete()
    return redirect('media_dashboard')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class MediaFileListCreate(generics.ListCreateAPIView):
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer

    def perform_create(self, serializer):
        # Associates the logged in user with the media file
        serializer.save(user=self.request.user)
