// Simple European Date Picker (DD.MM.YYYY format) with Dark/Cyan Theme
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date-input');
    if (!dateInput) return;

    // Create date picker container
    const pickerContainer = document.createElement('div');
    pickerContainer.id = 'date-picker';
    
    // 1. Updated Container (Dark Theme)
    pickerContainer.style.cssText = `
        position: absolute;
        background: #1e293b; /* Slate-800 */
        border: 2px solid #22d3ee; /* Cyan-400 */
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        padding: 15px;
        z-index: 1000;
        display: none;
        font-family: 'Inter', sans-serif;
        min-width: 280px;
        color: white; /* Force text to be white */
    `;

    // Create calendar header
    const header = document.createElement('div');
    header.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    `;

    // 2. Update Header Buttons (Cyan style)
    const buttonStyle = `
        border: none;
        background: #334155;
        color: #22d3ee;
        padding: 5px 12px;
        cursor: pointer;
        border-radius: 6px;
        font-weight: bold;
        font-size: 18px;
    `;

    const prevBtn = document.createElement('button');
    prevBtn.textContent = '‹';
    prevBtn.style.cssText = buttonStyle;

    const nextBtn = document.createElement('button');
    nextBtn.textContent = '›';
    nextBtn.style.cssText = buttonStyle;

    const monthYear = document.createElement('span');
    monthYear.style.cssText = `
        font-weight: bold;
        padding: 0 20px;
        color: #ffffff;
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

    // Day names (European style)
    const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    dayNames.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.textContent = day;
        dayEl.style.cssText = `
            text-align: center;
            padding: 5px;
            font-weight: bold;
            font-size: 12px;
            color: #94a3b8; /* Slate-400 */
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
        const parts = dateStr.split('.');
        if (parts.length !== 3) return new Date();
        const [day, month, year] = parts.map(Number);
        return new Date(year, month - 1, day);
    }

    function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        monthYear.textContent = `${['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'][month]} ${year}`;
        monthYear.style.color = "#ffffff"; // Force white header text

        // Clear existing days
        while (calendar.children.length > 7) {
            calendar.removeChild(calendar.lastChild);
        }

        const firstDay = new Date(year, month, 1);
        
        // Fix for European Monday-start
        let startOffset = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
        const startDate = new Date(year, month, 1);
        startDate.setDate(startDate.getDate() - startOffset);

        for (let i = 0; i < 42; i++) {
            const dayEl = document.createElement('button');
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);

            dayEl.textContent = date.getDate();
            
            // Bold Visibility Styles
            dayEl.style.cssText = `
                border: none;
                padding: 10px;
                cursor: pointer;
                border-radius: 6px;
                text-align: center;
                font-weight: 600;
                transition: all 0.2s;
                background: ${date.getMonth() === month ? '#334155' : '#1e293b'};
                color: ${date.getMonth() === month ? 'white' : '#64748b'};
            `;

            // Highlight Selected Date
            if (date.toDateString() === selectedDate.toDateString()) {
                dayEl.style.background = '#22d3ee'; // Cyan-400
                dayEl.style.color = '#000000';    // Dark text on bright background
            }

            // Hover effect
            dayEl.onmouseover = () => { 
                if(dayEl.style.background !== 'rgb(34, 211, 238)') dayEl.style.background = '#475569'; 
            };
            dayEl.onmouseout = () => { 
                if(dayEl.style.background !== 'rgb(34, 211, 238)') {
                    dayEl.style.background = (date.getMonth() === month ? '#334155' : '#1e293b');
                }
            };

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
        pickerContainer.style.top = (window.scrollY + rect.bottom + 5) + 'px';
        pickerContainer.style.display = 'block';
        renderCalendar();
    });

    prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // Close picker when clicking outside
    document.addEventListener('click', (e) => {
        if (!pickerContainer.contains(e.target) && e.target !== dateInput) {
            pickerContainer.style.display = 'none';
        }
    });

    // Initialize
    if (!dateInput.value) {
        dateInput.value = formatDate(new Date());
        selectedDate = new Date();
    } else {
        selectedDate = parseDate(dateInput.value);
        currentDate = new Date(selectedDate);
    }
});