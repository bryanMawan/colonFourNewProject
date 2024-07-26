class InfiniteScroll {
    constructor(containerSelector, eventAjaxUrl, formSelector, loadingComponentHtml, errorComponentHtml) {
        this.container = $(containerSelector)[0];
        this.eventAjaxUrl = eventAjaxUrl;
        this.formSelector = formSelector;
        this.loadingComponentHtml = loadingComponentHtml;
        this.errorComponentHtml = errorComponentHtml; // New property for error component
        this.offset = 0;
        this.limit = 4;
        this.isLoading = false;
        this.hasMore = true; // Flag to check if more events are available

        console.log("InfiniteScroll initialized.");
        console.log("Container:", this.container);
        console.log("Event AJAX URL:", this.eventAjaxUrl);

        this.bindEvents();
        this.loadEvents();
    }

    bindEvents() {
        $(document).ready(() => {
            $(this.formSelector).on('submit', (event) => this.handleFormSubmit(event));
            $(this.container).on('scroll', this.debounce(() => this.detectScroll(), 200));
        });
    }

    getUrlParams() {
        let params = {};
        let queryString = window.location.search.substring(1);
        let urlParams = new URLSearchParams(queryString);

        urlParams.forEach((value, key) => {
            params[key] = value;
        });

        return params;
    }

    getCombinedData() {
        let serializedFormData = $(this.formSelector).serialize();
        let urlParams = this.getUrlParams();
        let combinedData = serializedFormData;

        for (let key in urlParams) {
            if (urlParams.hasOwnProperty(key)) {
                combinedData += `&${encodeURIComponent(key)}=${encodeURIComponent(urlParams[key])}`;
            }
        }

        return combinedData;
    }

    loadEvents() {
        if (this.isLoading || !this.hasMore) {
            if (!this.hasMore) {
                console.warn("All events have been loaded.");
            } else {
                console.warn("Load events request already in progress.");
            }
            return;
        }

        console.log("loadEvents function called.");
        this.isLoading = true;
        this.showLoadingIndicator();

        $.ajax({
            url: this.eventAjaxUrl,
            method: 'GET',
            data: `${this.getCombinedData()}&offset=${this.offset}&limit=${this.limit}`,
            beforeSend: () => {
                console.log("AJAX request about to be sent.");
            },
            success: (response) => this.handleSuccess(response),
            error: (xhr, status, error) => this.handleError(xhr, status, error)
        });
    }

    handleSuccess(response) {
        console.log("AJAX request successful.");
        console.log("Response:", response);

        if (response.results && response.results.length > 0) {
            if (this.offset === 0) {
                $(this.container).empty();
            }

            response.results.forEach(event => {
                console.log("Processing event:", event);
                $(this.container).append(this.createEventCard(event));
            });

            this.offset += this.limit;
            updateScale();

            // Check if fewer results than the limit were returned
            if (response.results.length < this.limit) {
                console.log("Fewer results than limit, no more events to load.");
                this.hasMore = false;
            }
        } else {
            console.log("No more events to load.");
            this.hasMore = false;
        }

        this.isLoading = false;
        this.hideLoadingIndicator();
    }

    handleNoResults(response) {
        if (response.error) {
            console.error("Error in response:", response.error);
            $(this.container).append(this.errorComponentHtml); // Append the error card
        } else {
            console.warn("Unexpected response format:", response);
            $(this.container).append(this.errorComponentHtml); // Append the error card
        }
    }

    handleError(xhr, status, error) {
        console.error("AJAX request failed.");
        console.error("Status:", status);
        console.error("Error:", error);
        $(this.container).html(this.errorComponentHtml); // Use the error card HTML

        this.isLoading = false;
        this.hideLoadingIndicator();
    }

    createEventCard(event) {
        return `<div class="card position-relative" data-event-id="${event.id}" data-event-date="${event.formatted_date}" data-event-location="${event.location}">
                    ${event.poster_url ? `<img src="${event.poster_url}" alt="${event.name}" class="event-poster">` : ''}
                    <p class="event-name">${event.name}</p>
                    <span class="badge badge-goers rounded-pill">${event.get_number_of_goers} <span class="visually-hidden">goings</span></span>
                    <span class="badge badge-type rounded-pill">${event.get_event_type_display} <span class="visually-hidden">type</span></span>
                    <span class="badge badge-level rounded-pill">${event.level} <span class="visually-hidden">level</span></span>
                </div>`;
    }

    handleFormSubmit(event) {
        console.log("Form submitted.");
        event.preventDefault();
        this.offset = 0;
        this.hasMore = true; // Reset hasMore flag for new search
        this.loadEvents();
    }

    detectScroll() {
        console.log("Scroll event detected.");
    
        const scrollWidth = this.container.scrollWidth;
        const scrollLeft = this.container.scrollLeft;
        const containerWidth = this.container.clientWidth;
    
        console.log("Scroll Width:", scrollWidth);
        console.log("Scroll Left:", scrollLeft);
        console.log("Container Width:", containerWidth);
    
        if (scrollLeft + containerWidth >= scrollWidth - 10) {
            console.log("Scrolled to the end of the container.");
            this.loadEvents(); // Only call loadEvents, which already handles the checks
        }
    }

    updateScale() {
        console.log("Updating scale or any necessary post-load logic.");
    }

    showLoadingIndicator() {
        console.log("Showing loading indicator.");
        $(this.container).append(this.loadingComponentHtml);
    }

    hideLoadingIndicator() {
        console.log("Hiding loading indicator.");
        $(this.container).find('.card-spinner').remove();
    }

    debounce(func, wait) {
        let timeout;
        return function(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Instantiate the InfiniteScroll class
new InfiniteScroll('.scroll-container', eventAjaxUrl, '#search-form', '<div class="card card-spinner"><div class="spinner-grow" role="status"><span class="visually-hidden">Loading...</span></div></div>',     '<div class="card card-error"><div class="card-body"><p class="text-danger">An error occurred while loading events.</p></div></div>'
);
