# Smoke Tests

Smoke tests answer one cheap question: can the real application/package initialize far enough to prove that basic startup is not broken?

Build 01 should replace the initial package-import smoke test with the smallest safe Qt startup check that exercises the real application entry point without opening a normal interactive window.
