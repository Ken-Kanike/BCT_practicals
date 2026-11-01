const CoursePayment = artifacts.require("CoursePayment");

contract("CoursePayment", (accounts) => {
  const [owner, student, other] = accounts;
  const PRICE = web3.utils.toWei("0.5", "ether");
  let app;

  beforeEach(async () => {
    app = await CoursePayment.new({ from: owner });
    await app.addCourse("Blockchain Fundamentals", PRICE, { from: owner });
  });

  it("deploys with the correct owner and first course", async () => {
    assert.equal(await app.owner(), owner);
    assert.equal((await app.courseCount()).toString(), "1");

    const course = await app.getCourse(1);
    assert.equal(course.name, "Blockchain Fundamentals");
    assert.equal(course.price.toString(), PRICE);
    assert.equal(course.active, true);
  });

  it("allows only the owner to add a course", async () => {
    await app.addCourse("DeFi Essentials", web3.utils.toWei("1", "ether"), { from: owner });
    assert.equal((await app.courseCount()).toString(), "2");

    try {
      await app.addCourse("Unauthorized", PRICE, { from: student });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "Only owner");
    }
  });

  it("lets a student purchase a course and records the payment", async () => {
    const receipt = await app.purchaseCourse(1, { from: student, value: PRICE });

    assert.equal(await app.hasPurchased(student, 1), true);
    assert.equal((await app.paymentCount()).toString(), "1");
    assert.equal(await web3.eth.getBalance(app.address), PRICE);

    const payments = await app.getMyPayments({ from: student });
    assert.equal(payments.length, 1);
    assert.equal(payments[0].student, student);
    assert.equal(payments[0].courseId.toString(), "1");
    assert.equal(payments[0].amount.toString(), PRICE);

    const event = receipt.logs.find((log) => log.event === "CoursePurchased");
    assert.equal(event.args.student, student);
    assert.equal(event.args.courseId.toString(), "1");
    assert.equal(event.args.amount.toString(), PRICE);
  });

  it("rejects an incorrect payment amount", async () => {
    try {
      await app.purchaseCourse(1, {
        from: student,
        value: web3.utils.toWei("0.1", "ether"),
      });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "Incorrect payment");
    }
  });

  it("rejects duplicate purchases", async () => {
    await app.purchaseCourse(1, { from: student, value: PRICE });

    try {
      await app.purchaseCourse(1, { from: student, value: PRICE });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "already purchased");
    }
  });

  it("rejects purchases for unknown or inactive courses", async () => {
    try {
      await app.purchaseCourse(99, { from: student, value: PRICE });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "Unknown course");
    }

    await app.setCourseActive(1, false, { from: owner });
    try {
      await app.purchaseCourse(1, { from: student, value: PRICE });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "not active");
    }
  });

  it("allows only the owner to withdraw the contract balance", async () => {
    await app.purchaseCourse(1, { from: student, value: PRICE });

    try {
      await app.withdraw({ from: student });
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "Only owner");
    }

    const receipt = await app.withdraw({ from: owner });
    assert.equal(await web3.eth.getBalance(app.address), "0");

    const event = receipt.logs.find((log) => log.event === "Withdrawn");
    assert.equal(event.args.owner, owner);
    assert.equal(event.args.amount.toString(), PRICE);
  });

  it("returns payment history only for the calling student", async () => {
    await app.purchaseCourse(1, { from: student, value: PRICE });

    const studentPayments = await app.getMyPayments({ from: student });
    const otherPayments = await app.getMyPayments({ from: other });

    assert.equal(studentPayments.length, 1);
    assert.equal(otherPayments.length, 0);
  });

  it("exposes individual payments to the owner dashboard", async () => {
    await app.purchaseCourse(1, { from: student, value: PRICE });

    const payment = await app.getPayment(0);
    assert.equal(payment.student, student);
    assert.equal(payment.courseId.toString(), "1");
    assert.equal(payment.amount.toString(), PRICE);

    try {
      await app.getPayment(5);
      assert.fail("expected revert");
    } catch (error) {
      assert.include(error.message, "Invalid payment index");
    }
  });
});
