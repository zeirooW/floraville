-- to test this script u need to buy seeds and plant them at ur garden. if ur money = 0 or label just wait, my database needs some time to start working
local RS = game:GetService("ReplicatedStorage")
local Remotes = RS:FindFirstChild("Remotes")
local FlowersData = require(RS.src.shared.FlowersData) -- all  flowers data
local SoundServiceHandler = require(RS.src.shared.SoundServiceHandler)
local VFXHandler = require(RS.src.shared.VFXHandler)
local EnchantmentHandler = require(RS.src.shared.EnchantmentHandler)
local Utils = require(RS.src.shared.Utils) -- for the random functions
local HttpService = game:GetService("HttpService")
local SSS = game:GetService("ServerScriptService")
local IDhandler = require(SSS.src.IDHandler) -- gives an id to flower to find it's tool
local Codec = require(SSS.src.Codec) -- encodes/decodes the data to save it in the player data/inventory

local function SizeCFrameStageAttribute(stage) -- saves the old size and cframe of the stage
	local size
	local cf
	if not stage:GetAttribute("oldSize") then
		local Size = stage.Size
		stage:SetAttribute("oldSize", string.format("%f,%f,%f", Size.X, Size.Y, Size.Z))
		size = Size
	else
		local xyz = string.split(stage:GetAttribute("oldSize"), ",")
		size = Vector3.new(tonumber(xyz[1]), tonumber(xyz[2]), tonumber(xyz[3]))
	end
	
	if not stage:GetAttribute("oldCFrame") then
		local cframe = tostring(stage.CFrame)
		stage:SetAttribute("oldCFrame", cframe)
		cf = stage.CFrame
	else
		local values = string.split(stage:GetAttribute("oldCFrame"), ",")
		for i,v in ipairs(values) do
			values[i] = tonumber(v)
		end
		
		cf = CFrame.new(unpack(values))
	end
	
	return size, cf
end

local function Harvest(Base, Flower, FlowerData)--harvest function
	for i, v in pairs(Flower.Stages:GetDescendants()) do
		if v:IsA("ProximityPrompt") then
			v.Enabled = true

			v.Triggered:Connect(function(plr) -- harvest
				if plr.Name == Base.Owner.Value then
					SoundServiceHandler.MakeSound(RS.Sounds.Harvesting, v.Parent)
					
					local SaveAtts = {"Type", "Enchantments", "EnchantmentMultiplier", "BouquetMultiplier"}
					local ExcludeInst = {"ProximityPrompt"}
					local FlowerTool = Utils.FromModelToTool(Flower, ExcludeInst, SaveAtts)
					FlowerTool.Parent = plr.Backpack
					
					local ID = IDhandler.GetFlowerID()
					FlowerTool:SetAttribute("ID", "Flower"..ID)

					local FlowerValue = Instance.new("StringValue", plr.Inventory.Flowers)
					FlowerValue.Name = "Flower"..ID
					local PlantData = {}
					PlantData.FlowerName = FlowerData.Name
					PlantData.Scale = FlowerTool.Handle.Size.X / RS.Flowers[FlowerTool.Name].Handle.Size.X
					if FlowerTool:GetAttribute("Enchantments") then
						PlantData.Enchantments = HttpService:JSONDecode(FlowerTool:GetAttribute("Enchantments"))
					end
					FlowerValue.Value = Codec.EncodePlant(PlantData)
					
					local Length = Utils.GetFlowerLength(FlowerTool)
					FlowerTool.Name = FlowerTool.Name.." ["..Length.."]"
				end
			end)
		end
	end
end

local function Grow(Flower, FlowerData, Base, PlantedAt) -- grow + connect harvest function
	local cycles = FlowerData.Cycles
	local growtime = FlowerData.GrowTime
	local numstages = FlowerData.Stages
	
	local stages = Flower.Stages:GetChildren()
	local groupedstages = {}
	local keys = {}
	
	table.sort(stages, function(a,b) -- sorts by number
		return tonumber(a.Name) < tonumber(b.Name)
	end)

	for i, stage in pairs(stages) do -- groups by number
		local num = tonumber(stage.Name)
		groupedstages[num] = groupedstages[num] or {}
		table.insert(groupedstages[num], stage)
	end

	for i, stage in pairs(stages) do
		stage.Transparency = 1
	end
	
	local TimePassed
	if PlantedAt then
		TimePassed = os.time() - PlantedAt
	end
	
	local elapsed = 0
	if TimePassed and TimePassed > 0 then -- offline growth
		elapsed += TimePassed/(growtime/numstages)
	end
	
	elapsed = math.max(Flower:GetAttribute("Elapsed"), elapsed)
	
	local waterbonus = Flower:GetAttribute("WaterBonus") or 0 -- bonus by watering can
	elapsed += waterbonus/(growtime/numstages)
	Flower:SetAttribute("WaterBonus", 0)
	for stage = 1, numstages do
		for i, stagepart in pairs(groupedstages[stage]) do
			SizeCFrameStageAttribute(stagepart)
			stagepart.Transparency = 0
			stagepart.Size = Vector3.new(0,0,0)
		end
		
		while elapsed < 1 do
			local growrate = Flower:GetAttribute("GrowRate") or 1
			if Flower:GetAttribute("Growing") then
				elapsed = elapsed
			else
				elapsed = elapsed + 1/cycles
				Flower:SetAttribute("Growing", true)
				task.delay(growtime/numstages/cycles/growrate, function()
					Flower:SetAttribute("Growing", false)
				end)
			end
			
			Flower:SetAttribute("Elapsed", Flower:GetAttribute("Elapsed") + 1/cycles + waterbonus/(growtime/numstages))
			if elapsed >= 1 then
				break
			end
			
			for i, stagepart in pairs(groupedstages[stage]) do
				local OldSize, OldCFrame = SizeCFrameStageAttribute(stagepart)
				stagepart.Size = Vector3.new(OldSize.X * elapsed, OldSize.Y * elapsed, OldSize.Z * elapsed)
				stagepart.CFrame = OldCFrame * CFrame.new(0,-OldSize.Y/2 + OldSize.Y*elapsed/2,0)
			end
			
			task.wait(growtime/numstages/cycles/growrate)
		end
		
		if elapsed >= 1 then
			for i, stagepart in pairs(groupedstages[stage]) do
				local OldSize, OldCFrame = SizeCFrameStageAttribute(stagepart)
				stagepart.Size = OldSize
				stagepart.CFrame = OldCFrame
			end
			
			local att = Flower:GetAttribute("Elapsed")
			local value = math.max(elapsed, att)
			if value > numstages then
				value = numstages
			end

			Flower:SetAttribute("Elapsed", value)
			elapsed -= 1
		end	
	end
	
	local Player = game:GetService("Players"):FindFirstChild(Base.Owner.Value)
	if Player and Flower then
		Remotes.PlaySoundEvent:FireClient(Player, RS.Sounds.Grown, Flower.PrimaryPart.Position)
		Remotes.PlayEffectEvent:FireClient(Player, RS.VFX.GrowVFX, Flower.Bottom.Position)
		VFXHandler.SetEnabledTrue(Flower)
		Harvest(Base, Flower, FlowerData)
	end
end

local function Plant(FlowerName,FlowerModelData, Base) -- plant flower func
	local PlantedAt = FlowerModelData.OSTime or nil
	local Pos = FlowerModelData.Position or nil
	local Scale = FlowerModelData.Scale or nil
	local Ground = Base.GroundsFolder[FlowerModelData.Ground].Ground or nil
	local WaterBonus = FlowerModelData.WaterBonus or nil
	local Elapsed = FlowerModelData.Elapsed or nil
	local Enchants = HttpService:JSONEncode(FlowerModelData.Enchantments) or nil
	
	local FinalPosition
	local Player = game:GetService("Players"):FindFirstChild(Base.Owner.Value)
	
	local FlowerData = FlowersData.All[FlowerName]
	local FlowerModel = FlowerData.FlowerModel:Clone()
	FlowerModel:SetAttribute("Type", "Flower")
	
	if not PlantedAt then
		FinalPosition = Pos + Vector3.new(0,1,0)

		if EnchantmentHandler.EnchantOrNonEnchant() then
			local enchantment = EnchantmentHandler.RandomEnchantment()
			EnchantmentHandler.AddEnchantment(FlowerModel, enchantment)
		end
	else
		FinalPosition = Pos + Ground.Position
		if Enchants and Enchants ~= "null" then
			FlowerModel:SetAttribute("Enchantments", Enchants)
			EnchantmentHandler.AddEnchantmentsFromAttribute(FlowerModel)
		end
	end
	
	if not PlantedAt then
		RS.Remotes.PlaySoundEvent:FireClient(Player, RS.Sounds.Planting, FinalPosition)
	end
	
	if not Scale then
		local random = Random.new()
		FlowerModel:ScaleTo(random:NextNumber(1,1.25))
	else
		FlowerModel:ScaleTo(Scale)
	end

	FlowerModel.Parent = Ground
	FlowerModel:PivotTo(CFrame.new(FinalPosition.X, FinalPosition.Y, FinalPosition.Z) * CFrame.Angles(0, math.rad(math.random(0,360)), 0))
	
	local PlantedAtValue = PlantedAt or os.time()
	FlowerModel:SetAttribute("PlantedAt", PlantedAtValue)
	FlowerModel:SetAttribute("GrowRate", 1)
	
	if Elapsed then
		FlowerModel:SetAttribute("Elapsed", Elapsed)
	else
		FlowerModel:SetAttribute("Elapsed", 0)
	end
	
	if WaterBonus then
		FlowerModel:SetAttribute("WaterBonus", WaterBonus)
	else
		FlowerModel:SetAttribute("WaterBonus", 0)
	end

	for i, v in pairs(FlowerModel.Stages:GetDescendants()) do
		if v:IsA("ProximityPrompt") then
			v.Enabled = false
		end
	end
	
	VFXHandler.SetEnabledFalse(FlowerModel)
	local cor = coroutine.create(Grow)
	local debounce = false
	coroutine.resume(cor, FlowerModel, FlowerData, Base, PlantedAt)
	FlowerModel:GetAttributeChangedSignal("WaterBonus"):Connect(function() -- if watered - restart grow with water bonus
		if not debounce and not (FlowerModel:GetAttribute("Elapsed") / FlowerData.Stages >= 1) then
			debounce = true
			task.delay(2, function()
				debounce = false
			end)
			coroutine.close(cor)
			task.wait(2)
			PlantedAt = FlowerModel:GetAttribute("PlantedAt")
			cor = coroutine.create(Grow)
			coroutine.resume(cor, FlowerModel, FlowerData, Base, PlantedAt)
		end
	end)
	
	FlowerModel:GetAttributeChangedSignal("GrowRate"):Connect(function() -- if added a fertilizer - restart grow with fertilzer bonus	
		if not debounce and not (FlowerModel:GetAttribute("Elapsed") / FlowerData.Stages >= 1) then
			debounce = true
			task.delay(2, function()
				debounce = false
			end)
			coroutine.close(cor)
			task.wait(2)
			PlantedAt = FlowerModel:GetAttribute("PlantedAt")
			cor = coroutine.create(Grow)
			coroutine.resume(cor, FlowerModel, FlowerData, Base, PlantedAt)
		end
	end)
end

Remotes.Plant.OnServerEvent:Connect(function(plr, groundmodel, mousehit)
	local Base 
	local FlowerName
	for i,v in ipairs(workspace:GetChildren()) do
		if v:FindFirstChild("Owner") and v.Owner.Value == plr.Name then
			Base = v
			break
		end
	end

	for i,tool in pairs(plr.Character:GetChildren()) do
		if tool:IsA("Tool") and Base:FindFirstChild("GroundsFolder")[groundmodel.Name]:FindFirstChild("Bought").Value and tool.Name:find("Seed") then
			local StringPos = tool.Name:find("Seed")
			if FlowersData.All[tool.Name:sub(1, StringPos - 1)] then
				FlowerName = tool.Name:sub(1, StringPos - 1)
				if plr.Inventory.Seeds:FindFirstChild(tool.Name:sub(1, StringPos + 3)).Value > 1 then
					plr.Inventory.Seeds[tool.Name:sub(1, StringPos + 3)].Value = plr.Inventory.Seeds[tool.Name:sub(1, StringPos + 3)].Value - 1
					tool.Name = tool.Name:sub(1, StringPos + 3).." ["..plr.Inventory.Seeds[tool.Name:sub(1, StringPos + 3)].Value.."x]"
				else
					plr.Inventory.Seeds[tool.Name:sub(1, StringPos + 3)]:Destroy()
					tool:Destroy() -- tool.Name:sub(1, StringPos + 3) : RoseSeed [2x] --> RoseSeed
				end
			end
			
			local RP = RaycastParams.new()
			RP.FilterType = Enum.RaycastFilterType.Include
			RP.FilterDescendantsInstances = {groundmodel}

			local origin = mousehit.Position + Vector3.new(0,1,0)
			local direction = Vector3.new(0,-2,0)
			local result = workspace:Raycast(origin, direction, RP)

			if result and groundmodel.Parent.Parent:FindFirstChild("Owner") and groundmodel.Parent.Parent.Owner.Value == plr.Name and Base:FindFirstChild("GroundsFolder")[groundmodel.Name] then
				local FlowerModelData = {
					["Position"] = mousehit.Position;
					["Ground"] = groundmodel.Name
				}
				Plant(FlowerName,FlowerModelData, Base)	
			end
		end
	end
end)

RS.Bindable.GrowOffline.Event:Connect(function(plr, FlowerName, FlowerModelData) -- considers growth offline
	local Base 
	for i,v in ipairs(workspace:GetChildren()) do
		if v:FindFirstChild("Owner") and v.Owner.Value == plr.Name then
			Base = v
			break
		end
	end

	Plant(FlowerName, FlowerModelData, Base) -- PlantedAt ~= nil
end)

