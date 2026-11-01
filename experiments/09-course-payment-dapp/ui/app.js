const RPC_URL = "http://127.0.0.1:7545";
const NETWORK = { chainId: 1337, name: "ganache" };

const els = {
  networkLabel: document.getElementById("network-label"),
  networkId: document.getElementById("network-id"),
  studentAddress: document.getElementById("student-address"),
  ownerAddress: document.getElementById("owner-address"),
  contractAddress: document.getElementById("contract-address"),
  courseCount: document.getElementById("course-count"),
  paymentTotal: document.getElementById("payment-total"),
  contractBalanceHero: document.getElementById("contract-balance-hero"),
  contractBalance: document.getElementById("contract-balance"),
  catalogPill: document.getElementById("catalog-pill"),
  paymentPill: document.getElementById("payment-pill"),
  courses: document.getElementById("courses"),
  payments: document.getElementById("payments"),
  withdraw: document.getElementById("withdraw"),
  addCourseForm: document.getElementById("add-course"),
  courseName: document.getElementById("course-name"),
  coursePrice: document.getElementById("course-price"),
  status: document.getElementById("status"),
};

const state = {
  contract: null,
  provider: null,
  ownerSigner: null,
  studentSigner: null,
  owner: "",
  student: "",
  deployment: null,
  courses: [],
  busy: false,
};

let statusTimer = null;

function short(address) {
  return `${address.slice(0, 6)}…${address.slice(-4)}`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[character]));
}

function setStatus(message, type = "") {
  clearTimeout(statusTimer);
  els.status.textContent = message;
  els.status.className = `status show ${type}`;
  if (type === "success") {
    statusTimer = setTimeout(() => {
      els.status.className = "status";
    }, 6000);
  }
}

async function init() {
  try {
    if (!window.ethers) {
      throw new Error("Ethers.js failed to load from vendor/ethers.umd.min.js");
    }

    const response = await fetch("deployment.json");
    if (!response.ok) {
      throw new Error("deployment.json not found. Run `truffle migrate` first.");
    }

    state.deployment = await response.json();
    state.provider = new ethers.JsonRpcProvider(RPC_URL, NETWORK);
    state.contract = new ethers.Contract(
      state.deployment.address,
      state.deployment.abi,
      state.provider
    );
    state.ownerSigner = await state.provider.getSigner(0);
    state.studentSigner = await state.provider.getSigner(1);
    state.owner = await state.ownerSigner.getAddress();
    state.student = await state.studentSigner.getAddress();

    els.studentAddress.textContent = short(state.student);
    els.ownerAddress.textContent = short(state.owner);
    els.contractAddress.textContent = short(state.deployment.address);
    els.networkId.textContent = `#${state.deployment.networkId}`;
    els.networkLabel.textContent = `Ganache #${state.deployment.networkId}`;

    await refresh();
    setStatus("Connected to the course payment contract.", "success");
  } catch (error) {
    setStatus(error.shortMessage || error.message, "error");
  }
}

async function refresh() {
  const count = Number(await state.contract.courseCount());
  const courses = [];

  for (let courseId = 1; courseId <= count; courseId += 1) {
    const [name, price, active] = await state.contract.getCourse(courseId);
    const purchased = await state.contract.hasPurchased(state.student, courseId);
    courses.push({ id: courseId, name, price, active, purchased });
  }

  state.courses = courses;
  renderCourses(courses);

  const payments = await state.contract.connect(state.studentSigner).getMyPayments();
  renderPayments(payments);

  const balance = await state.provider.getBalance(state.deployment.address);
  const balanceText = `${ethers.formatEther(balance)} ETH`;

  els.courseCount.textContent = count;
  els.paymentTotal.textContent = payments.length;
  els.contractBalanceHero.textContent = balanceText;
  els.contractBalance.textContent = balanceText;
  els.catalogPill.textContent = `${count} course${count === 1 ? "" : "s"}`;
  els.paymentPill.textContent = `${payments.length} receipt${payments.length === 1 ? "" : "s"}`;
}

function renderCourses(courses) {
  if (!courses.length) {
    els.courses.innerHTML =
      '<p class="empty">No courses yet. The owner can add one from the dashboard.</p>';
    return;
  }

  els.courses.innerHTML = courses
    .map((course) => {
      const price = ethers.formatEther(course.price);
      const statusClass = course.active ? "" : " off";
      const statusText = course.active ? "Active" : "Inactive";
      const disabled = !course.active || course.purchased || state.busy;
      const buttonText = course.purchased
        ? "Purchased"
        : course.active
        ? "Purchase"
        : "Inactive";

      return `
        <article class="course-card">
          <div class="course-top">
            <span class="course-index">${String(course.id).padStart(2, "0")}</span>
            <span class="status-tag${statusClass}">${statusText}</span>
          </div>
          <h4>${escapeHtml(course.name)}</h4>
          <div class="course-price">${price}<span>ETH</span></div>
          <div class="course-meta">
            <span style="font-size: 11px; color: #64748b;">
              ${course.purchased ? "On-chain receipt available" : "Lifetime access"}
            </span>
            <button
              class="btn btn-primary buy"
              data-id="${course.id}"
              data-price="${course.price}"
              ${disabled ? "disabled" : ""}
            >${buttonText}</button>
          </div>
        </article>
      `;
    })
    .join("");

  els.courses.querySelectorAll("button.buy").forEach((button) => {
    button.addEventListener("click", () =>
      purchase(Number(button.dataset.id), button.dataset.price)
    );
  });
}

function renderPayments(payments) {
  if (!payments.length) {
    els.payments.innerHTML =
      '<p class="empty">No payments yet. Purchase a course to create an on-chain receipt.</p>';
    return;
  }

  els.payments.innerHTML = payments
    .map((payment) => {
      const courseId = Number(payment.courseId);
      const course = state.courses.find((item) => item.id === courseId);
      const name = course ? course.name : `Course #${courseId}`;
      const amount = ethers.formatEther(payment.amount);
      const date = new Date(Number(payment.timestamp) * 1000).toLocaleString();

      return `
        <div class="payment-item">
          <strong>${escapeHtml(name)}</strong>
          <span class="amount">${amount} ETH</span>
          <span class="meta">Paid ${date} · course #${courseId}</span>
        </div>
      `;
    })
    .join("");
}

async function purchase(courseId, price) {
  if (state.busy) return;
  state.busy = true;

  try {
    setStatus(`Sending purchase transaction for course #${courseId}…`, "pending");
    const tx = await state.contract
      .connect(state.studentSigner)
      .purchaseCourse(courseId, { value: price });
    setStatus(`Transaction ${short(tx.hash)} sent. Waiting for confirmation…`, "pending");
    await tx.wait();
    setStatus("Purchase confirmed on-chain.", "success");
    await refresh();
  } catch (error) {
    setStatus(error.shortMessage || error.message, "error");
  } finally {
    state.busy = false;
  }
}

async function withdraw() {
  if (state.busy) return;
  state.busy = true;

  try {
    setStatus("Sending withdrawal transaction…", "pending");
    const tx = await state.contract.connect(state.ownerSigner).withdraw();
    setStatus(`Transaction ${short(tx.hash)} sent. Waiting for confirmation…`, "pending");
    await tx.wait();
    setStatus("Withdrawal confirmed. Funds transferred to the owner.", "success");
    await refresh();
  } catch (error) {
    setStatus(error.shortMessage || error.message, "error");
  } finally {
    state.busy = false;
  }
}

async function addCourse(event) {
  event.preventDefault();
  if (state.busy) return;

  const name = els.courseName.value.trim();
  const priceInput = els.coursePrice.value.trim();
  if (!name || !priceInput) return;

  state.busy = true;

  try {
    const price = ethers.parseEther(priceInput);
    setStatus(`Adding “${name}” to the catalog…`, "pending");
    const tx = await state.contract.connect(state.ownerSigner).addCourse(name, price);
    await tx.wait();
    setStatus("Course added on-chain.", "success");
    els.addCourseForm.reset();
    await refresh();
  } catch (error) {
    setStatus(error.shortMessage || error.message, "error");
  } finally {
    state.busy = false;
  }
}

els.withdraw.addEventListener("click", withdraw);
els.addCourseForm.addEventListener("submit", addCourse);
init();
