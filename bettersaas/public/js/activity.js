$(document).ready(function () {
    let interval = setInterval(function () {
        let timelineItem = document.querySelector('.timeline-item');

        if (timelineItem) {
            if (timelineItem.querySelector('.ai-generate-wrapper')) {
                clearInterval(interval);
                return;
            }

            let wrapper = document.createElement('div');
            wrapper.className = 'ai-generate-wrapper';

            let mainBtn = document.createElement('button');
            mainBtn.className = 'btn btn-xs btn-secondary action-btn';
            mainBtn.innerHTML = `
                <i class="fa fa-star" style="margin-right: 4px;"></i>
                Ask AI
            `;
            let dropdown = document.createElement('div');
            dropdown.className = 'ai-generate-dropdown';

            let summarizeBtn = document.createElement('button');
            summarizeBtn.className = 'btn btn-xs btn-secondary';
            summarizeBtn.innerHTML = `
                <i class="fa fa-list" style="margin-right: 4px;"></i>
                Summarize
            `;
            summarizeBtn.onclick = () => {
                window.CRMCopilotWidget.open(); 
                window.CRMCopilotWidget.sendMessage("Hello");
            }

            // let writeEmailBtn = document.createElement('button');
            // writeEmailBtn.className = 'btn btn-xs btn-secondary';
            // writeEmailBtn.textContent = 'Write Email';
            // writeEmailBtn.onclick = () => frappe.msgprint('Write Email clicked!');

            dropdown.appendChild(summarizeBtn);
            // dropdown.appendChild(writeEmailBtn);

            mainBtn.onclick = function (e) {
                e.stopPropagation();
                dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
            };

            document.addEventListener('click', function () {
                dropdown.style.display = 'none';
            });

            wrapper.appendChild(mainBtn);
            wrapper.appendChild(dropdown);
            timelineItem.appendChild(wrapper);

            clearInterval(interval);
        }
    }, 300);
});
