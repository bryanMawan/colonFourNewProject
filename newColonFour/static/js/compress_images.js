document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('battleForm');
    const infoPicsInput = document.getElementById('id_info_pics_carousel');
    const posterInput = document.getElementById('id_poster');

    async function compressImage(file, quality) {
        return new Promise((resolve, reject) => {
            console.debug(`Original size of ${file.name}: ${file.size / 1024} KB`);
            new Compressor(file, {
                quality: quality, // Adjust quality as needed
                success(result) {
                    console.debug(`Compressed size of ${result.name}: ${result.size / 1024} KB`);
                    // Convert Blob back to File object
                    const compressedFile = new File([result], file.name, {
                        type: result.type,
                        lastModified: Date.now()
                    });
                    resolve(compressedFile);
                },
                error(err) {
                    console.error('Image compression error:', err);
                    reject(err);
                },
            });
        });
    }

    async function compressFiles(inputField, maxTotalSizeMB) {
        const compressedFiles = [];
        const filesToCompress = [...inputField.files];
        let totalSizeMB = 0;
        let quality = 0.65;

        while (true) {
            totalSizeMB = 0;
            compressedFiles.length = 0; // Reset compressed files array

            for (let file of filesToCompress) {
                try {
                    const compressedFile = await compressImage(file, quality);
                    compressedFiles.push(compressedFile);
                    totalSizeMB += compressedFile.size / (1024 * 1024); // Convert size to MB
                } catch (err) {
                    console.error('Error compressing image:', err);
                }
            }

            if (totalSizeMB <= maxTotalSizeMB) {
                break;
            }

            // Reduce quality and retry
            quality -= 0.1;
            if (quality <= 0.1) {
                console.error('Cannot compress images below acceptable quality');
                break;
            }
            console.debug(`Total size exceeded ${maxTotalSizeMB}MB, reducing quality to ${quality}`);
        }

        // Replace original files with compressed files
        const dataTransfer = new DataTransfer();
        compressedFiles.forEach(file => dataTransfer.items.add(file));
        inputField.files = dataTransfer.files;
    }

    async function handleImageCompression(event) {
        event.preventDefault();

        console.time('Image Compression Time'); // Start timing

        // Compress info_pics_carousel files
        if (infoPicsInput.files.length > 0) {
            await compressFiles(infoPicsInput, 3); // 4MB max total size
        }

        // Compress poster file separately
        if (posterInput.files.length > 0) {
            await compressFiles(posterInput, 1); // Adjust if needed for poster alone
        }

        console.timeEnd('Image Compression Time'); // End timing and print result

        // Debug print to check final form data
        console.debug('Final form data before submit:', new FormData(form));

        // Submit the form
        form.submit();
    }

    form.addEventListener('submit', handleImageCompression);
});
