--!strict
-- TideMath.luau -- deterministic, side-effect-free tide and gangway kinematics.
-- Distances are metres; angles are radians. Keep this module free of Roblox services
-- so the same equations can be checked independently of the runtime.

local TideMath = {}

export type TideSpec = {
	lowM: number,
	highM: number,
	periodSeconds: number,
	phaseRadians: number?,
}

export type GangwaySpec = {
	shoreZ_M: number,
	deckOffsetM: number,
	spanM: number,
	referenceTideM: number,
	directionX: number,
}

local TAU = 2 * math.pi

function TideMath.levelAt(spec: TideSpec, elapsedSeconds: number): number
	assert(spec.periodSeconds > 0, "tide period must be positive")
	assert(spec.highM >= spec.lowM, "high tide must not be below low tide")
	local phase = TAU * (elapsedSeconds / spec.periodSeconds) + (spec.phaseRadians or 0)
	local fraction = (1 - math.cos(phase)) * 0.5
	return spec.lowM + (spec.highM - spec.lowM) * fraction
end

function TideMath.gangwayAngle(tideM: number, spec: GangwaySpec): number
	assert(spec.spanM > 0, "gangway span must be positive")
	assert(math.abs(spec.directionX) == 1, "gangway directionX must be -1 or +1")
	-- Solve the chord pitch from the fixed shore hinge to the moving deck end.
	-- directionX is the sign of the span's Blender X direction. For the Victoria
	-- gangways (-X from shore), positive Roblox Z rotation lowers the outer end.
	local dz = tideM + spec.deckOffsetM - spec.shoreZ_M
	return math.atan(dz / (spec.directionX * spec.spanM))
end

function TideMath.referenceAngle(spec: GangwaySpec): number
	return TideMath.gangwayAngle(spec.referenceTideM, spec)
end

function TideMath.bogieSlideM(tideM: number, spec: GangwaySpec): number
	local targetAngle = TideMath.gangwayAngle(tideM, spec)
	local baseAngle = TideMath.referenceAngle(spec)
	-- Horizontal endpoint displacement on the pontoon's longitudinal track.
	-- directionX is +1 or -1 in the exported Blender X direction.
	return spec.directionX * spec.spanM * (math.cos(targetAngle) - math.cos(baseAngle))
end

return TideMath
