// Simple European Date Picker (DD.MM.YYYY format)
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date-input');
    if (!dateInput) return;

    // Create date picker container
    const pickerContainer = document.createElement('div');
    pickerContainer.id = 'date-picker';
    pickerContainer.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 10px;
        z-index: 1000;
        display: none;
        font-family: Arial, sans-serif;
        min-width: 250px;
    `;

    // Create calendar header
    const header = document.createElement('div');
    header.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    `;

    const prevBtn = document.createElement('button');
    prevBtn.textContent = '‹';
    prevBtn.style.cssText = `
        border: none;
        background: #f0f0f0;
        padding: 5px 10px;
        cursor: pointer;
        border-radius: 3px;
    `;

    const nextBtn = document.createElement('button');
    nextBtn.textContent = '›';
    nextBtn.style.cssText = prevBtn.style.cssText;

    const monthYear = document.createElement('span');
    monthYear.style.cssText = `
        font-weight: bold;
        padding: 0 20px;
    `;

    header.appendChild(prevBtn);
    header.appendChild(monthYear);
    header.appendChild(nextBtn);

    // Create calendar grid
    const calendar = document.createElement('div');
    calendar.style.cssText = `
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
    `;

    // Day names
    const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    dayNames.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.textContent = day;
        dayEl.style.cssText = `
            text-align: center;
            padding: 5px;
            font-weight: bold;
            font-size: 12px;
        `;
        calendar.appendChild(dayEl);
    });

    pickerContainer.appendChild(header);
    pickerContainer.appendChild(calendar);
    document.body.appendChild(pickerContainer);

    let currentDate = new Date();
    let selectedDate = new Date();

    function formatDate(date) {
        const day = ('0' + date.getDate()).slice(-2);
        const month = ('0' + (date.getMonth() + 1)).slice(-2);
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    function parseDate(dateStr) {
        const [day, month, year] = dateStr.split('.').map(Number);
        return new Date(year, month - 1, day);
    }

    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        monthYear.textContent = `${['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'][month]} ${year}`;

        // Clear existing days
        while (calendar.children.length > 7) {
            calendar.removeChild(calendar.lastChild);
        }

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay() + 1); // Start from Monday

        for (let i = 0; i < 42; i++) {
            const dayEl = document.createElement('button');
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);

            dayEl.textContent = date.getDate();
            dayEl.style.cssText = `
                border: none;
                background: ${date.getMonth() === month ? 'white' : '#f5f5f5'};
                padding: 8px;
                cursor: pointer;
                border-radius: 3px;
                text-align: center;
                min-width: 30px;
            `;

            if (date.toDateString() === selectedDate.toDateString()) {
                dayEl.style.background = '#007bff';
                dayEl.style.color = 'white';
            }

            dayEl.addEventListener('click', () => {
                selectedDate = new Date(date);
                dateInput.value = formatDate(selectedDate);
                pickerContainer.style.display = 'none';
            });

            calendar.appendChild(dayEl);
        }
    }

    // Event listeners
    dateInput.addEventListener('click', function(e) {
        e.stopPropagation();
        const rect = dateInput.getBoundingClientRect();
        pickerContainer.style.left = rect.left + 'px';
        pickerContainer.style.top = (rect.bottom + 5) + 'px';
        pickerContainer.style.display = 'block';
        renderCalendar();
    });

    prevBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // Close picker when clicking outside
    document.addEventListener('click', (e) => {
        if (!pickerContainer.contains(e.target) && e.target !== dateInput) {
            pickerContainer.style.display = 'none';
        }
    });

    // Initialize with today's date if empty
    if (!dateInput.value) {
        dateInput.value = formatDate(new Date());
        selectedDate = new Date();
    } else {
        selectedDate = parseDate(dateInput.value);
    }
});
