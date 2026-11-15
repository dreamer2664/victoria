--!nonstrict
--[[
	Effects.lua -- smoke, steam and spray.

	Victorian steam plant smokes: a coal-fired boiler under load throws a
	visible plume, the safety valve lifts, and the exhaust beats with the
	engine.  The emitters are built in code so they do not have to be authored
	in Studio, and are driven by the controller's engine state.
]]

local Effects = {}

local function emitter(parent, name, props)
	local e = Instance.new("ParticleEmitter")
	e.Name = name
	for k, v in pairs(props) do
		e[k] = v
	end
	e.Parent = parent
	return e
end

--- Coal smoke from the funnel crown.
function Effects.funnelSmoke(funnelTip)
	local e = emitter(funnelTip, "Smoke", {
		Texture = "rbxasset://textures/particles/smoke_main.dds",
		Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, Color3.fromRGB(70, 68, 66)),
			ColorSequenceKeypoint.new(0.5, Color3.fromRGB(120, 118, 116)),
			ColorSequenceKeypoint.new(1, Color3.fromRGB(190, 190, 190)),
		}),
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.6),
			NumberSequenceKeypoint.new(0.35, 2.4),
			NumberSequenceKeypoint.new(1, 5.2),
		}),
		Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.25),
			NumberSequenceKeypoint.new(0.6, 0.62),
			NumberSequenceKeypoint.new(1, 1),
		}),
		Lifetime = NumberRange.new(2.2, 3.6),
		Speed = NumberRange.new(3.0, 5.0),
		SpreadAngle = Vector2.new(8, 8),
		Rotation = NumberRange.new(-20, 20),
		RotSpeed = NumberRange.new(-14, 14),
		Acceleration = Vector3.new(0, 4.5, 0),
		LightEmission = 0.05,
		Rate = 0,
		Enabled = true,
	})
	return e
end

--- White steam: whistle, safety valve, drain cocks.
function Effects.steamJet(parent, opts)
	opts = opts or {}
	return emitter(parent, opts.name or "Steam", {
		Texture = "rbxasset://textures/particles/sparkles_main.dds",
		Color = ColorSequence.new(Color3.fromRGB(240, 240, 245)),
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.25),
			NumberSequenceKeypoint.new(0.5, 1.4),
			NumberSequenceKeypoint.new(1, 3.0),
		}),
		Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.15),
			NumberSequenceKeypoint.new(1, 1),
		}),
		Lifetime = NumberRange.new(0.7, 1.4),
		Speed = NumberRange.new(opts.speed or 9, (opts.speed or 9) + 4),
		SpreadAngle = Vector2.new(opts.spread or 12, opts.spread or 12),
		Acceleration = Vector3.new(0, 6, 0),
		Rate = 0,
		Enabled = true,
	})
end

--- Water thrown off the bow as the boat gets under way.
function Effects.bowSpray(attachment)
	local e = emitter(attachment, "Spray", {
		Texture = "rbxasset://textures/particles/sparkles_main.dds",
		Color = ColorSequence.new(Color3.fromRGB(226, 236, 240)),
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.35),
			NumberSequenceKeypoint.new(1, 1.6),
		}),
		Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.25),
			NumberSequenceKeypoint.new(1, 1),
		}),
		Lifetime = NumberRange.new(0.4, 0.9),
		Speed = NumberRange.new(4, 8),
		SpreadAngle = Vector2.new(35, 12),
		Rate = 0,
		Enabled = true,
	})
	return e
end

--- Wake/churn behind the propeller.
function Effects.propWash(attachment)
	local e = emitter(attachment, "Wash", {
		Texture = "rbxasset://textures/particles/sparkles_main.dds",
		Color = ColorSequence.new(Color3.fromRGB(215, 230, 235)),
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.4),
			NumberSequenceKeypoint.new(1, 2.2),
		}),
		Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.3),
			NumberSequenceKeypoint.new(1, 1),
		}),
		Lifetime = NumberRange.new(0.5, 1.1),
		Speed = NumberRange.new(6, 11),
		SpreadAngle = Vector2.new(28, 28),
		Rate = 0,
		Enabled = true,
	})
	return e
end

return Effects
