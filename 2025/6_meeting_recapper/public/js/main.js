document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("upload-form");
  const meetingFile = document.getElementById("meeting-file");
  const fileUploadLabel = document.querySelector(".file-upload-label span");
  const fileName = document.querySelector(".file-name");
  const progressBar = document.querySelector(".progress-bar");
  const statusMessage = document.querySelector(".status-message");
  const meetingsContainer = document.getElementById("meetings-container");
  const meetingDetails = document.getElementById("meeting-details");
  const backToMeetingsBtn = document.getElementById("back-to-meetings");

  // Load meetings on page load
  loadMeetings();

  meetingFile.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      fileName.textContent = file.name;
      fileUploadLabel.textContent = "File selected";
    } else {
      fileName.textContent = "";
      fileUploadLabel.textContent = "Choose a file or drag it here";
    }
  });

  // File drag and drop functionality
  const fileUpload = document.querySelector(".file-upload");

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    fileUpload.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    fileUpload.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    fileUpload.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    fileUpload.classList.add("highlight");
  }

  function unhighlight() {
    fileUpload.classList.remove("highlight");
  }

  fileUpload.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      meetingFile.files = files;
      fileName.textContent = files[0].name;
      fileUploadLabel.textContent = "File selected";
    }
  }

  // Form submission
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const titleInput = document.getElementById("meeting-title");
    const title = titleInput.value;
    const file = meetingFile.files[0];

    if (!title || !file) {
      statusMessage.textContent = "Please provide a title and file";
      statusMessage.classList.add("error");
      return;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("meeting", file);

    progressBar.style.width = "0%";
    statusMessage.textContent = "Uploading...";
    statusMessage.classList.remove("error");
    statusMessage.classList.add("uploading");

    try {
      // Simulate upload progress (in a real app, use XHR with progress event)
      const progressInterval = setInterval(() => {
        const currentWidth = parseInt(progressBar.style.width) || 0;
        if (currentWidth < 90) {
          progressBar.style.width = currentWidth + 5 + "%";
        }
      }, 500);

      // Upload the file
      const response = await fetch("/api/meetings/upload", {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const result = await response.json();

      progressBar.style.width = "100%";
      statusMessage.textContent =
        "Processing your meeting. This may take a few minutes...";
      statusMessage.classList.remove("uploading");
      statusMessage.classList.add("success");

      // Reset form after successful upload
      setTimeout(() => {
        uploadForm.reset();
        fileName.textContent = "";
        fileUploadLabel.textContent = "Choose a file or drag it here";
        progressBar.style.width = "0%";
        statusMessage.textContent = "";
        statusMessage.className = "status-message";

        // Reload meetings list
        loadMeetings();
      }, 3000);
    } catch (error) {
      console.error("Upload error:", error);
      progressBar.style.width = "0%";
      statusMessage.textContent = "Error: " + error.message;
      statusMessage.classList.remove("uploading");
      statusMessage.classList.add("error");
    }
  });

  async function loadMeetings() {
    meetingsContainer.innerHTML =
      '<div class="loading-spinner"><i class="fas fa-spinner fa-pulse"></i></div>';

    try {
      const response = await fetch("/api/meetings");
      const meetings = await response.json();

      if (meetings.length === 0) {
        meetingsContainer.innerHTML =
          '<div class="no-meetings">No meetings found. Upload your first meeting recording!</div>';
        return;
      }

      let meetingsHTML = "";

      meetings.forEach((meeting) => {
        const date = new Date(meeting.created_at).toLocaleDateString();
        const duration = meeting.duration
          ? formatDuration(meeting.duration)
          : "Processing...";

        meetingsHTML += `
            <div class="meeting-card" data-id="${meeting.id}">
              <div class="meeting-card-header">
                <h3>${meeting.title}</h3>
                <span class="meeting-date">${date}</span>
              </div>
              <div class="meeting-card-body">
                <p><i class="far fa-clock"></i> ${duration}</p>
                <button class="btn btn-secondary view-meeting">
                  <i class="fas fa-chart-bar"></i> View Analysis
                </button>
              </div>
            </div>
          `;
      });

      meetingsContainer.innerHTML = meetingsHTML;

      // Add event listeners to view meeting buttons
      document.querySelectorAll(".view-meeting").forEach((button) => {
        button.addEventListener("click", function () {
          const meetingId = this.closest(".meeting-card").dataset.id;
          showMeetingDetails(meetingId);
        });
      });
    } catch (error) {
      console.error("Error loading meetings:", error);
      meetingsContainer.innerHTML =
        '<div class="error-message">Failed to load meetings. Please try again.</div>';
    }
  }

  function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  }

  async function showMeetingDetails(meetingId) {
    try {
      document.getElementById("meeting-detail-title").textContent =
        "Loading...";
      document.getElementById("meeting-date").textContent = "";
      document.getElementById("meeting-duration").textContent = "";
      document.getElementById("speaker-chart").innerHTML =
        '<div class="loading-spinner"><i class="fas fa-spinner fa-pulse"></i></div>';
      document.getElementById("sentiment-chart").innerHTML =
        '<div class="loading-spinner"><i class="fas fa-spinner fa-pulse"></i></div>';
      document.getElementById("topics-chart").innerHTML =
        '<div class="loading-spinner"><i class="fas fa-spinner fa-pulse"></i></div>';
      document.getElementById("action-items").innerHTML =
        '<div class="loading-spinner"><i class="fas fa-spinner fa-pulse"></i></div>';

      document.getElementById("meetings-list").classList.add("hidden");
      document.getElementById("upload-section").classList.add("hidden");
      meetingDetails.classList.remove("hidden");

      const response = await fetch(`/api/meetings/${meetingId}`);
      const data = await response.json();

      document.getElementById("meeting-detail-title").textContent =
        data.meeting.title;
      document.getElementById("meeting-date").textContent = new Date(
        data.meeting.created_at
      ).toLocaleDateString();
      document.getElementById("meeting-duration").textContent = data.meeting
        .duration
        ? `Duration: ${formatDuration(data.meeting.duration)}`
        : "";

      renderSpeakerChart(data.speakers);
      renderSentimentTimeline(data.segments);
      renderTopicsTimeline(data.topics);
      renderActionItems(data.actionItems);
    } catch (error) {
      console.error("Error loading meeting details:", error);
      document.getElementById("meeting-detail-title").textContent =
        "Error loading meeting";
      document.getElementById("speaker-chart").innerHTML =
        '<div class="error-message">Failed to load data</div>';
      document.getElementById("sentiment-chart").innerHTML =
        '<div class="error-message">Failed to load data</div>';
      document.getElementById("topics-chart").innerHTML =
        '<div class="error-message">Failed to load data</div>';
      document.getElementById("action-items").innerHTML =
        '<div class="error-message">Failed to load data</div>';
    }
  }

  backToMeetingsBtn.addEventListener("click", () => {
    meetingDetails.classList.add("hidden");
    document.getElementById("meetings-list").classList.remove("hidden");
    document.getElementById("upload-section").classList.remove("hidden");
  });

  // D3.js Visualization Rendering Functions

  // 1. Speaker Distribution Chart (Pie Chart)
  function renderSpeakerChart(speakers) {
    if (!speakers || speakers.length === 0) {
      document.getElementById("speaker-chart").innerHTML =
        '<div class="no-data">No speaker data available</div>';
      return;
    }

    const container = document.getElementById("speaker-chart");
    container.innerHTML = "";

    const width = container.clientWidth;
    const height = 300;
    const radius = Math.min(width, height) / 2;

    const svg = d3
      .select(container)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const pie = d3
      .pie()
      .value((d) => d.speaking_time)
      .sort(null);

    const arc = d3
      .arc()
      .innerRadius(0)
      .outerRadius(radius * 0.8);

    const outerArc = d3
      .arc()
      .innerRadius(radius * 0.9)
      .outerRadius(radius * 0.9);

    const arcs = svg
      .selectAll(".arc")
      .data(pie(speakers))
      .enter()
      .append("g")
      .attr("class", "arc");

    arcs
      .append("path")
      .attr("d", arc)
      .attr("fill", (d, i) => color(i))
      .attr("stroke", "white")
      .style("stroke-width", "2px")
      .style("opacity", 0.7);

    const text = svg
      .selectAll(".labels")
      .data(pie(speakers))
      .enter()
      .append("text")
      .attr("dy", ".35em")
      .text((d) => `Speaker ${d.data.speaker_id}`);

    function midAngle(d) {
      return d.startAngle + (d.endAngle - d.startAngle) / 2;
    }

    text
      .attr("transform", (d) => {
        const pos = outerArc.centroid(d);
        pos[0] = radius * (midAngle(d) < Math.PI ? 1 : -1);
        return `translate(${pos})`;
      })
      .style("text-anchor", (d) => (midAngle(d) < Math.PI ? "start" : "end"))
      .style("font-size", "12px");

    const polyline = svg
      .selectAll(".lines")
      .data(pie(speakers))
      .enter()
      .append("polyline")
      .attr("points", (d) => {
        const pos = outerArc.centroid(d);
        pos[0] = radius * 0.95 * (midAngle(d) < Math.PI ? 1 : -1);
        return [arc.centroid(d), outerArc.centroid(d), pos];
      })
      .style("fill", "none")
      .style("stroke", "#999")
      .style("stroke-width", "1px");

    svg
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "0em")
      .text("Speaker")
      .style("font-size", "16px");

    svg
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "1.2em")
      .text("Distribution")
      .style("font-size", "16px");
  }

  // 2. Sentiment Timeline (Line Chart)
  function renderSentimentTimeline(segments) {
    if (!segments || segments.length === 0) {
      document.getElementById("sentiment-chart").innerHTML =
        '<div class="no-data">No sentiment data available</div>';
      return;
    }

    const container = document.getElementById("sentiment-chart");
    container.innerHTML = "";

    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 280 - margin.top - margin.bottom;

    const svg = d3
      .select(container)
      .append("svg")
      .attr("width", container.clientWidth)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // X scale (time)
    const x = d3
      .scaleLinear()
      .domain([0, d3.max(segments, (d) => d.end_time)])
      .range([0, width]);

    // Y scale (sentiment score: -1 to 1)
    const y = d3.scaleLinear().domain([-1, 1]).range([height, 0]);

    // Add X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height / 2})`)
      .call(
        d3
          .axisBottom(x)
          .tickFormat((d) => formatDuration(d))
          .ticks(5)
      );

    // Add Y axis
    svg.append("g").call(d3.axisLeft(y));

    // Add horizontal line at y=0
    svg
      .append("line")
      .attr("x1", 0)
      .attr("y1", y(0))
      .attr("x2", width)
      .attr("y2", y(0))
      .style("stroke", "#ccc")
      .style("stroke-dasharray", "3,3");

    // Add the sentiment line
    const line = d3
      .line()
      .x((d) => x((d.start_time + d.end_time) / 2))
      .y((d) => y(d.sentiment))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(segments)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add sentiment points
    svg
      .selectAll(".sentiment-point")
      .data(segments)
      .enter()
      .append("circle")
      .attr("class", "sentiment-point")
      .attr("cx", (d) => x((d.start_time + d.end_time) / 2))
      .attr("cy", (d) => y(d.sentiment))
      .attr("r", 3)
      .attr("fill", (d) =>
        d.sentiment > 0 ? "#4CAF50" : d.sentiment < 0 ? "#F44336" : "#FFC107"
      )
      .attr("stroke", "white");

    // Add labels for axis
    svg
      .append("text")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(${width / 2},${height + margin.bottom})`)
      .text("Time")
      .style("font-size", "12px");

    svg
      .append("text")
      .attr("text-anchor", "middle")
      .attr("transform", "rotate(-90)")
      .attr("y", -margin.left + 10)
      .attr("x", -height / 2)
      .text("Sentiment")
      .style("font-size", "12px");
  }

  // 2. Topics table
  function renderTopicsTimeline(topics) {
    if (!topics || topics.length === 0) {
      document.getElementById("topics-chart").innerHTML =
        '<div class="no-data">No topic data available</div>';
      return;
    }

    const container = document.getElementById("topics-chart");

    const durations = topics.map((topic) => topic.end_time - topic.start_time);
    const maxDuration = Math.max(...durations);

    topics.forEach((topic) => {
      const duration = topic.end_time - topic.start_time;
      topic.relevance = ((duration / maxDuration) * 25).toFixed(2);
    });

    topics.sort((a, b) => b.relevance - a.relevance);

    let tableHTML = `
      <div class="topics-table-container" style="max-height: 280px; overflow-y: auto;">
        <table class="topics-table" style="width: 100%; border-collapse: collapse;">
          <thead style="position: sticky; top: 0; background-color: white;">
            <tr>
              <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Topic</th>
              <th style="padding: 8px; text-align: center; border-bottom: 2px solid #ddd;">Relevance</th>
              <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Time</th>
            </tr>
          </thead>
          <tbody>
    `;

    topics.forEach((topic) => {
      const relevancePercent = Math.min(parseFloat(topic.relevance), 100);

      tableHTML += `
        <tr>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${
            topic.topic
          }</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">
            <div style="background-color: #eee; border-radius: 5px; height: 10px; width: 100%;">
              <div style="background-color: #4285f4; border-radius: 5px; height: 10px; width: ${relevancePercent}%;"></div>
            </div>
            <div style="text-align: center; margin-top: 4px; font-size: 12px;">${
              topic.relevance
            }</div>
          </td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
            ${formatDuration(topic.start_time)}
          </td>
        </tr>
      `;
    });

    tableHTML += `
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = tableHTML;
  }

  // 4. Action Items List
  function renderActionItems(actionItems) {
    const container = document.getElementById("action-items");

    if (!actionItems || actionItems.length === 0) {
      container.innerHTML = '<div class="no-data">No action items found</div>';
      return;
    }

    let html = '<ul class="action-items-list">';

    actionItems.forEach((item) => {
      html += `
          <li class="action-item">
            <div class="action-item-text">${item.text}</div>
            <div class="action-item-meta">
              <span class="action-assignee">
                <i class="fas fa-user"></i> ${item.assignee || "Not assigned"}
              </span>
              <span class="action-time">
                <i class="far fa-clock"></i> ${formatDuration(item.start_time)}
              </span>
            </div>
          </li>
        `;
    });

    html += "</ul>";
    container.innerHTML = html;
  }
});
