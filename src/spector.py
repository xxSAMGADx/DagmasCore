#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Spector GPU Debugging & Frame Analysis Engine
Default standard tool for WebGL, WebGPU, Babylon.js, and 3D graphics debugging.
Enables GPU draw call inspection, shader compile verification, state change auditing,
and 60 FPS performance profiling without third-party cloud tools.
"""

import json
from typing import Dict, Any, List

class SpectorInspector:
    """Spector.js GPU command capture, draw call analysis, and shader debugger."""

    def __init__(self, target_canvas: str = "renderCanvas", max_draw_calls: int = 150):
        self.target_canvas = target_canvas
        self.max_draw_calls = max_draw_calls

    def generate_injection_script(self, auto_capture: bool = True) -> str:
        """
        Generates client-side Spector.js injection snippet for Babylon.js / WebGL / WebGPU scenes.
        Can be embedded in HTML heads or executed via Playwright CDP.
        """
        auto_run = f"""
            spector.displayUI();
            spector.spyCanvases();
            console.log("[Spector] Attached to canvas: {self.target_canvas}");
        """ if auto_capture else "spector.displayUI();"

        return f"""
        <script src="https://spectorcdn.babylonjs.com/spector.bundle.js"></script>
        <script>
            var spector = new SPECTOR.Spector();
            {auto_run}
        </script>
        """.strip()

    def analyze_frame(self, draw_calls: int, fps: float, total_triangles: int,
                      shader_switches: int = 0, textures_bound: int = 0) -> Dict[str, Any]:
        """
        Evaluates GPU frame telemetry against 60 FPS production standards.
        Flags rendering bottlenecks, high draw call counts, and excessive shader switches.
        """
        issues: List[str] = []
        status = "OPTIMAL"

        # 1. Framerate evaluation
        if fps < 55.0:
            status = "DEGRADED"
            issues.append(f"Framerate below 60 FPS target: {fps:.1f} FPS")

        # 2. Draw Call Budgeting
        if draw_calls > self.max_draw_calls:
            status = "BOTTLENECK"
            issues.append(
                f"Draw call budget exceeded: {draw_calls} calls (target: <= {self.max_draw_calls}). Consider instancing or batching."
            )

        # 3. Shader State Thrashing
        if shader_switches > (draw_calls * 0.7):
            issues.append(f"Excessive shader pipeline switches: {shader_switches} switches for {draw_calls} draw calls.")

        # 4. Geometry density
        if total_triangles > 500000:
            issues.append(f"High polycount: {total_triangles:,} triangles. Consider LOD or mesh decimation.")

        return {
            "status": status,
            "fps": fps,
            "draw_calls": draw_calls,
            "shader_switches": shader_switches,
            "total_triangles": total_triangles,
            "textures_bound": textures_bound,
            "within_budget": len(issues) == 0,
            "recommendations": issues if issues else ["Frame adheres to 60 FPS performance ceiling."]
        }

    def generate_mock_report(self) -> Dict[str, Any]:
        """Generates sample GPU profiling telemetry for diagnostics."""
        return self.analyze_frame(
            draw_calls=48,
            fps=60.0,
            total_triangles=45000,
            shader_switches=8,
            textures_bound=12
        )


class ADHDSkillSkeptor:
    """
    Hyper-focus single-task lock combined with Spector.js 60 FPS GPU profiling.
    Prevents context drift, audits off-target distractions, and enforces WebGL/WebGPU
    framerate ceilings.
    """

    def __init__(self, inspector: SpectorInspector = None):
        self.inspector = inspector or SpectorInspector()
        self.active_goal: str = ""
        self.distraction_count: int = 0
        self.locked: bool = False

    def set_focus_goal(self, goal: str) -> Dict[str, Any]:
        """Locks agent attention onto a single high-priority milestone."""
        self.active_goal = goal.strip()
        self.locked = True
        return {
            "status": "LOCKED",
            "active_goal": self.active_goal,
            "hyperfocus_mode": True
        }

    def audit_action(self, action_description: str) -> Dict[str, Any]:
        """Audits proposed agent steps against the hyper-focus lock to block rabbit-holes."""
        if not self.locked or not self.active_goal:
            return {"allowed": True, "reason": "No active hyperfocus lock set."}

        action_lower = action_description.lower()
        goal_keywords = [w for w in self.active_goal.lower().split() if len(w) > 3]

        # Check keyword affinity or off-topic rabbit-holing
        matches = [kw for kw in goal_keywords if kw in action_lower]
        is_aligned = len(matches) > 0 or len(goal_keywords) == 0

        if not is_aligned:
            self.distraction_count += 1
            return {
                "allowed": False,
                "warning": f"Distraction detected! Proposed action '{action_description}' deviates from locked goal '{self.active_goal}'.",
                "distraction_strikes": self.distraction_count
            }

        return {
            "allowed": True,
            "status": "ALIGNED",
            "active_goal": self.active_goal
        }

    def complete_goal(self) -> Dict[str, Any]:
        """Releases the hyperfocus lock after verified milestone completion."""
        prev = self.active_goal
        self.active_goal = ""
        self.locked = False
        return {
            "status": "COMPLETED",
            "previous_goal": prev,
            "distractions_blocked": self.distraction_count
        }

    def profile_graphics_fps(self, draw_calls: int, fps: float, total_triangles: int) -> Dict[str, Any]:
        """Audits WebGL/WebGPU graphics performance using SpectorInspector."""
        return self.inspector.analyze_frame(draw_calls=draw_calls, fps=fps, total_triangles=total_triangles)


# Canonical alias
ADHDSkillSpector = ADHDSkillSkeptor


if __name__ == "__main__":
    spector = SpectorInspector()
    print("Spector.js Default Graphics Tool Diagnostic:")
    report = spector.generate_mock_report()
    print(json.dumps(report, indent=2))

